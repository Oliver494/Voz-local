from pathlib import Path
import json
import logging
import os
import shutil
import uuid
from typing import Literal

from fastapi import FastAPI, File, Form, HTTPException, Query, Request, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.concurrency import run_in_threadpool
import soundfile as sf
import numpy as np

from .audio import combine_wav, normalize_reference, process_generated_audio, split_script, wav_to_mp3
from .engine import ModelError, engine
from .runtime import runtime_info
from .voice_settings import VoiceSettings, settings_from_json
from . import storage


logging.basicConfig(level=logging.INFO)
storage.initialize()
app = FastAPI(title="Voz Local", docs_url=None, redoc_url=None)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["127.0.0.1", "localhost", "testserver"])
app.mount("/static", StaticFiles(directory=storage.ROOT / "static"), name="static")


@app.middleware("http")
async def check_origin(request: Request, call_next):
    if request.method in {"POST", "PATCH", "PUT", "DELETE"}:
        origin = request.headers.get("origin")
        if origin and origin not in {"http://127.0.0.1:8765", "http://localhost:8765"}:
            return JSONResponse({"detail": "Origen no permitido."}, status_code=403)
    return await call_next(request)


def new_id() -> str:
    return uuid.uuid4().hex


def require_project(project_id: str) -> dict:
    project = storage.one("SELECT * FROM projects WHERE id = ?", (project_id,))
    if not project:
        raise HTTPException(404, "No encuentro ese proyecto.")
    return project


def require_chunk(project_id: str, chunk_id: str) -> dict:
    chunk = storage.one(
        "SELECT * FROM chunks WHERE id = ? AND project_id = ?", (chunk_id, project_id)
    )
    if not chunk:
        raise HTTPException(404, "No encuentro ese fragmento.")
    return chunk


def public_chunk(chunk: dict) -> dict:
    result = dict(chunk)
    result.pop("audio_path", None)
    path = storage.DATA / chunk["audio_path"] if chunk["audio_path"] else None
    raw = storage.PROJECTS / chunk["project_id"] / f"{chunk['id']}.raw.wav"
    playback = raw if path and raw.is_file() else path
    result["audio_url"] = (
        f"/api/projects/{chunk['project_id']}/chunks/{chunk['id']}/audio?v={playback.stat().st_mtime_ns}"
        if playback and playback.is_file() else None
    )
    result["raw_audio_url"] = (
        f"/api/projects/{chunk['project_id']}/chunks/{chunk['id']}/raw-audio?v={raw.stat().st_mtime_ns}"
        if result["audio_url"] and raw.is_file() else None
    )
    previous = storage.PROJECTS / chunk["project_id"] / f"{chunk['id']}.anterior.wav"
    result["previous_audio_url"] = (
        f"/api/projects/{chunk['project_id']}/chunks/{chunk['id']}/previous-audio?v={previous.stat().st_mtime_ns}"
        if previous.is_file() else None
    )
    previous_raw = storage.PROJECTS / chunk["project_id"] / f"{chunk['id']}.anterior.raw.wav"
    result["previous_raw_audio_url"] = (
        f"/api/projects/{chunk['project_id']}/chunks/{chunk['id']}/previous-raw-audio?v={previous_raw.stat().st_mtime_ns}"
        if result["previous_audio_url"] and previous_raw.is_file() else None
    )
    return result


@app.get("/")
def home():
    return FileResponse(storage.ROOT / "static" / "index.html")


@app.get("/api/installation/download")
def download_installation():
    archive = storage.ROOT / "dist" / "Voz-Local.zip"
    if not archive.is_file():
        raise HTTPException(404, "El paquete de instalación todavía no está preparado.")
    return FileResponse(archive, media_type="application/zip", filename="Voz-Local.zip")


@app.get("/api/status")
def status():
    try:
        runtime = runtime_info()
        gpu_names, gpu_available = runtime['gpus'], runtime['gpu_available']
    except Exception as error:
        gpu_names, gpu_available = [], False
        runtime = {'backend': 'Unavailable', 'device': None, 'error': str(error)}
    voice_model_id = "Qwen/Qwen3-TTS-12Hz-1.7B-Base"
    voice_model_dir = storage.MODELS / "Qwen3-TTS-12Hz-1.7B-Base"
    voice_model_installed = all(
        (voice_model_dir / filename).is_file()
        for filename in ("model.safetensors", "speech_tokenizer/model.safetensors")
    )
    return {
        "gpu_available": gpu_available,
        "gpus": gpu_names,
        "runtime": runtime,
        "target_model": engine.preferred_size,
        "active_model": engine.active_size,
        "model_downloaded": voice_model_installed,
        "voice_model": {
            "id": voice_model_id,
            "installed": voice_model_installed,
            "active_size": engine.active_size,
        },
        "ollama_available": bool(engine.ollama_models()),
    }


@app.get("/api/voices")
def list_voices():
    return storage.all_rows(
        """SELECT v.*, (SELECT COUNT(*) FROM projects WHERE voice_id = v.id) AS project_count
           FROM voices v ORDER BY v.created_at DESC, v.id DESC"""
    )


@app.post("/api/voices")
async def create_voice(
    name: str = Form(...), transcript: str = Form(...), file: UploadFile = File(...)
):
    name, transcript = name.strip(), transcript.strip()
    if not 1 <= len(name) <= 80:
        raise HTTPException(400, "Pon un nombre de entre 1 y 80 caracteres.")
    if not 1 <= len(transcript) <= 2000:
        raise HTTPException(400, "Escribe el texto exacto que se oye en la muestra.")
    voice_id = new_id()
    source = storage.TMP / f"{voice_id}.upload"
    destination = storage.VOICES / f"{voice_id}.wav"
    size = 0
    try:
        with source.open("wb") as output:
            while piece := await file.read(1024 * 1024):
                size += len(piece)
                if size > 30 * 1024 * 1024:
                    raise HTTPException(413, "El audio no puede superar 30 MB.")
                output.write(piece)
        if not size:
            raise HTTPException(400, "El archivo de audio está vacío.")
        try:
            duration = await run_in_threadpool(normalize_reference, source, destination)
        except ValueError as error:
            raise HTTPException(400, str(error)) from error
        destination.chmod(0o600)
        with storage.connection() as db:
            db.execute(
                "INSERT INTO voices (id, name, transcript, sample_path, duration) VALUES (?, ?, ?, ?, ?)",
                (voice_id, name, transcript, str(destination.relative_to(storage.DATA)), duration),
            )
        return storage.one("SELECT * FROM voices WHERE id = ?", (voice_id,))
    except Exception:
        if destination.exists() and not storage.one("SELECT id FROM voices WHERE id = ?", (voice_id,)):
            destination.unlink()
        raise
    finally:
        source.unlink(missing_ok=True)
        await file.close()


@app.get("/api/voices/{voice_id}/audio")
def voice_audio(voice_id: str):
    voice = storage.one("SELECT * FROM voices WHERE id = ?", (voice_id,))
    if not voice:
        raise HTTPException(404, "No encuentro esa voz.")
    path = storage.DATA / voice["sample_path"]
    return FileResponse(path, media_type="audio/wav", headers={"Cache-Control": "no-store"})


class VoiceTranscriptInput(BaseModel):
    transcript: str = Field(min_length=1, max_length=2000)


@app.patch("/api/voices/{voice_id}/transcript")
def set_voice_transcript(voice_id: str, payload: VoiceTranscriptInput):
    transcript = payload.transcript.strip()
    if not transcript:
        raise HTTPException(400, "Escribe exactamente lo que se oye en la muestra.")
    with engine.lock:
        if not storage.one("SELECT id FROM voices WHERE id = ?", (voice_id,)):
            raise HTTPException(404, "No encuentro ese perfil de voz.")
        with storage.connection() as db:
            db.execute(
                "UPDATE voices SET transcript = ? WHERE id = ?",
                (transcript, voice_id),
            )
        engine.prompt_cache = {
            key: value for key, value in engine.prompt_cache.items() if key[1] != voice_id
        }
    return storage.one("SELECT * FROM voices WHERE id = ?", (voice_id,))


class VoiceDeleteInput(BaseModel):
    project_ids: list[str]


@app.delete("/api/voices/{voice_id}")
def delete_voice(voice_id: str, payload: VoiceDeleteInput):
    with engine.lock:
        voice = storage.one("SELECT * FROM voices WHERE id = ?", (voice_id,))
        if not voice:
            raise HTTPException(404, "No encuentro ese perfil de voz.")
        linked_ids = [
            row["id"] for row in storage.all_rows(
                "SELECT id FROM projects WHERE voice_id = ? ORDER BY id", (voice_id,)
            )
        ]
        if linked_ids != sorted(payload.project_ids):
            raise HTTPException(409, "Los proyectos de esta voz han cambiado. Actualiza la página y vuelve a intentarlo.")
        with storage.connection() as db:
            db.executemany("DELETE FROM projects WHERE id = ?", [(project_id,) for project_id in linked_ids])
            db.execute("DELETE FROM voices WHERE id = ?", (voice_id,))
        engine.prompt_cache = {
            key: value for key, value in engine.prompt_cache.items() if key[1] != voice_id
        }
        for project_id in linked_ids:
            cleanup_project_files(project_id)
        try:
            (storage.DATA / voice["sample_path"]).unlink(missing_ok=True)
        except OSError:
            logging.exception("No se pudo limpiar la muestra de voz %s", voice_id)
    return {"deleted": True, "projects_deleted": len(linked_ids)}


class ProjectInput(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    voice_id: str
    script: str = Field(min_length=1, max_length=30000)
    mode: Literal["fragments", "continuous"] = "fragments"
    voice_model: Literal["qwen-1.7b", "qwen-0.6b", "qwen-0.6b-eco"] = "qwen-1.7b"


@app.get("/api/projects")
def list_projects():
    return storage.all_rows(
        """SELECT p.id, p.title, p.voice_id, p.mode, v.name AS voice_name, p.created_at, p.updated_at,
                  (SELECT COUNT(*) FROM chunks WHERE project_id = p.id) AS chunk_count
           FROM projects p JOIN voices v ON p.voice_id = v.id
           ORDER BY p.updated_at DESC, p.id DESC"""
    )


@app.post("/api/projects")
def create_project(payload: ProjectInput):
    with engine.lock:
        return _create_project(payload)


def _create_project(payload: ProjectInput):
    if not storage.one("SELECT id FROM voices WHERE id = ?", (payload.voice_id,)):
        raise HTTPException(400, "Selecciona una voz guardada.")
    title, script = payload.title.strip(), payload.script.strip()
    if not title or not script:
        raise HTTPException(400, "El título y el guion son obligatorios.")
    parts = split_script(script)
    if not parts or len(parts) > 200:
        raise HTTPException(400, "El guion es demasiado largo: admite hasta 200 partes de generación.")
    chunks = [script] if payload.mode == "continuous" else parts
    project_id = new_id()
    with storage.connection() as db:
        db.execute(
            "INSERT INTO projects (id, title, voice_id, script, mode, settings) VALUES (?, ?, ?, ?, ?, ?)",
            (project_id, title, payload.voice_id, script, payload.mode,
             VoiceSettings(model=payload.voice_model).model_dump_json()),
        )
        db.executemany(
            "INSERT INTO chunks (id, project_id, position, text) VALUES (?, ?, ?, ?)",
            [(new_id(), project_id, index, text) for index, text in enumerate(chunks)],
        )
    return get_project(project_id)


@app.get("/api/projects/{project_id}")
def get_project(project_id: str):
    project = require_project(project_id)
    voice = storage.one("SELECT name FROM voices WHERE id = ?", (project["voice_id"],))
    chunks = storage.all_rows(
        "SELECT * FROM chunks WHERE project_id = ? ORDER BY position", (project_id,)
    )
    return {**project, "settings": settings_from_json(project["settings"]).model_dump(),
            "voice_name": voice["name"] if voice else "", "chunks": [public_chunk(c) for c in chunks]}


@app.patch("/api/projects/{project_id}/settings")
def update_project_settings(project_id: str, payload: VoiceSettings):
    with engine.lock:
        require_project(project_id)
        with storage.connection() as db:
            db.execute("UPDATE projects SET settings = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                       (payload.model_dump_json(), project_id))
    return payload.model_dump()


class ProjectModeInput(BaseModel):
    mode: Literal["fragments", "continuous"]


@app.patch("/api/projects/{project_id}/mode")
def change_project_mode(project_id: str, payload: ProjectModeInput):
    with engine.lock:
        project = require_project(project_id)
        if project["mode"] == payload.mode:
            return {"project": get_project(project_id), "copied": False}
        parts = split_script(project["script"])
        if not parts or len(parts) > 200:
            raise HTTPException(400, "El guion es demasiado largo: admite hasta 200 partes de generación.")
        chunks = storage.all_rows("SELECT * FROM chunks WHERE project_id = ?", (project_id,))
        directory = storage.PROJECTS / project_id
        has_audio = any(chunk["audio_path"] for chunk in chunks) or (directory.exists() and any(directory.glob("*.wav")))
        if has_audio:
            label = "Audio completo" if payload.mode == "continuous" else "Por fragmentos"
            title = f"{project['title']} · {label}"[:120]
            copy = _create_project(ProjectInput(
                title=title, voice_id=project["voice_id"], script=project["script"], mode=payload.mode
            ))
            with storage.connection() as db:
                db.execute("UPDATE projects SET settings = ? WHERE id = ?", (project["settings"], copy["id"]))
            return {"project": get_project(copy["id"]), "copied": True}
        new_chunks = [project["script"]] if payload.mode == "continuous" else parts
        with storage.connection() as db:
            db.execute("DELETE FROM chunks WHERE project_id = ?", (project_id,))
            db.executemany(
                "INSERT INTO chunks (id, project_id, position, text) VALUES (?, ?, ?, ?)",
                [(new_id(), project_id, index, text) for index, text in enumerate(new_chunks)],
            )
            db.execute(
                "UPDATE projects SET mode = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (payload.mode, project_id),
            )
        return {"project": get_project(project_id), "copied": False}


@app.delete("/api/projects/{project_id}")
def delete_project(project_id: str):
    with engine.lock:
        require_project(project_id)
        with storage.connection() as db:
            db.execute("DELETE FROM projects WHERE id = ?", (project_id,))
        cleanup_project_files(project_id)
    return {"deleted": True}


def cleanup_project_files(project_id: str) -> None:
    try:
        shutil.rmtree(storage.PROJECTS / project_id)
    except FileNotFoundError:
        pass
    except OSError:
        logging.exception("No se pudo limpiar el audio del proyecto %s", project_id)
    for extension in ("wav", "mp3"):
        for version in ("", ".current", ".previous"):
            try:
                (storage.EXPORTS / f"{project_id}{version}.{extension}").unlink(missing_ok=True)
            except OSError:
                logging.exception("No se pudo limpiar una exportación del proyecto %s", project_id)


class ChunkInput(BaseModel):
    text: str = Field(min_length=1, max_length=30000)


@app.patch("/api/projects/{project_id}/chunks/{chunk_id}")
def edit_chunk(project_id: str, chunk_id: str, payload: ChunkInput):
    with engine.lock:
        return _edit_chunk(project_id, chunk_id, payload)


def _edit_chunk(project_id: str, chunk_id: str, payload: ChunkInput):
    project = require_project(project_id)
    chunk = require_chunk(project_id, chunk_id)
    text = payload.text.strip()
    if not text:
        raise HTTPException(400, "El fragmento no puede estar vacío.")
    if project["mode"] == "fragments" and len(text) > 350:
        raise HTTPException(400, "Un fragmento no puede superar 350 caracteres.")
    if project["mode"] == "continuous" and len(split_script(text)) > 200:
        raise HTTPException(400, "El guion es demasiado largo: admite hasta 200 partes de generación.")
    if text == chunk["text"]:
        return public_chunk(chunk)
    old_path = storage.DATA / chunk["audio_path"] if chunk["audio_path"] else None
    with storage.connection() as db:
        db.execute(
            "UPDATE chunks SET text = ?, audio_path = NULL, model_size = NULL WHERE id = ?",
            (text, chunk_id),
        )
        current = db.execute(
            "SELECT text FROM chunks WHERE project_id = ? ORDER BY position", (project_id,)
        ).fetchall()
        db.execute(
            "UPDATE projects SET script = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            ("\n".join(row["text"] for row in current), project_id),
        )
    if old_path:
        old_path.unlink(missing_ok=True)
        (storage.PROJECTS / project_id / f"{chunk_id}.raw.wav").unlink(missing_ok=True)
    return public_chunk(require_chunk(project_id, chunk_id))


@app.post("/api/projects/{project_id}/chunks/{chunk_id}/generate")
def generate_chunk(project_id: str, chunk_id: str):
    with engine.lock:
        return _generate_chunk(project_id, chunk_id)


def _generate_chunk(project_id: str, chunk_id: str):
    project = require_project(project_id)
    settings = settings_from_json(project["settings"])
    chunk = require_chunk(project_id, chunk_id)
    voice = storage.one("SELECT * FROM voices WHERE id = ?", (project["voice_id"],))
    if not voice:
        raise HTTPException(404, "La muestra de voz de este proyecto ya no existe.")
    directory = storage.PROJECTS / project_id
    directory.mkdir(parents=True, exist_ok=True, mode=0o700)
    output = directory / f"{chunk_id}.wav"
    previous = directory / f"{chunk_id}.anterior.wav"
    temporary = directory / f"{chunk_id}.tmp.wav"
    raw_output = directory / f"{chunk_id}.raw.wav"
    previous_raw = directory / f"{chunk_id}.anterior.raw.wav"
    raw_temporary = directory / f"{chunk_id}.tmp.raw.wav"
    try:
        parts = split_script(chunk["text"]) if project["mode"] == "continuous" else [chunk["text"]]
        writer = None
        raw_writer = None
        sample_rate = None
        model_size = None
        try:
            for index, part in enumerate(parts):
                wave, part_rate, model_size = engine.generate(
                    voice["id"], storage.DATA / voice["sample_path"], voice["transcript"], part, settings
                )
                if writer is None:
                    sample_rate = part_rate
                    writer = sf.SoundFile(temporary, mode="w", samplerate=sample_rate, channels=1, subtype="PCM_16")
                    raw_writer = sf.SoundFile(raw_temporary, mode="w", samplerate=sample_rate, channels=1, subtype="PCM_16")
                elif part_rate != sample_rate:
                    raise RuntimeError("Los fragmentos internos tienen frecuencias de audio distintas.")
                if index:
                    pause = np.zeros(round(sample_rate * 0.12), dtype=np.float32)
                    writer.write(pause)
                    raw_writer.write(pause)
                writer.write(np.asarray(wave, dtype=np.float32))
                raw_writer.write(np.asarray(wave, dtype=np.float32))
        finally:
            if writer is not None:
                writer.close()
            if raw_writer is not None:
                raw_writer.close()
        if require_chunk(project_id, chunk_id)["text"] != chunk["text"]:
            raise HTTPException(409, "El texto cambió durante la generación. Vuelve a generar este fragmento.")
        if output.is_file():
            shutil.copy2(output, previous)
            previous.chmod(0o600)
            if raw_output.is_file():
                shutil.copy2(raw_output, previous_raw)
                previous_raw.chmod(0o600)
            else:
                previous_raw.unlink(missing_ok=True)
        os.replace(temporary, output)
        os.replace(raw_temporary, raw_output)
        output.chmod(0o600)
        raw_output.chmod(0o600)
        with storage.connection() as db:
            db.execute(
                "UPDATE chunks SET audio_path = ?, model_size = ? WHERE id = ?",
                (str(output.relative_to(storage.DATA)), model_size, chunk_id),
            )
            db.execute(
                "UPDATE projects SET updated_at = CURRENT_TIMESTAMP WHERE id = ?", (project_id,)
            )
        return public_chunk(require_chunk(project_id, chunk_id))
    except ModelError as error:
        raise HTTPException(503, str(error)) from error
    except RuntimeError as error:
        raise HTTPException(500, str(error)) from error
    finally:
        temporary.unlink(missing_ok=True)
        raw_temporary.unlink(missing_ok=True)


@app.get("/api/projects/{project_id}/chunks/{chunk_id}/audio")
def chunk_audio(project_id: str, chunk_id: str):
    chunk = require_chunk(project_id, chunk_id)
    if not chunk["audio_path"]:
        raise HTTPException(404, "Este fragmento todavía no tiene audio.")
    original = storage.PROJECTS / project_id / f"{chunk_id}.raw.wav"
    path = original if original.is_file() else storage.DATA / chunk["audio_path"]
    if not path.is_file():
        raise HTTPException(404, "No encuentro el archivo de audio.")
    return FileResponse(path, media_type="audio/wav", headers={"Cache-Control": "no-store"})


@app.get("/api/projects/{project_id}/chunks/{chunk_id}/raw-audio")
def raw_chunk_audio(project_id: str, chunk_id: str):
    chunk = require_chunk(project_id, chunk_id)
    path = storage.PROJECTS / project_id / f"{chunk_id}.raw.wav"
    if not chunk["audio_path"] or not path.is_file():
        raise HTTPException(404, "Esta versión no conserva el audio original. Genérala de nuevo para compararlo.")
    return FileResponse(path, media_type="audio/wav", headers={"Cache-Control": "no-store"})


@app.get("/api/projects/{project_id}/chunks/{chunk_id}/previous-audio")
def previous_chunk_audio(project_id: str, chunk_id: str):
    require_chunk(project_id, chunk_id)
    path = storage.PROJECTS / project_id / f"{chunk_id}.anterior.wav"
    if not path.is_file():
        raise HTTPException(404, "Este fragmento no tiene una versión anterior.")
    return FileResponse(path, media_type="audio/wav", headers={"Cache-Control": "no-store"})


@app.get("/api/projects/{project_id}/chunks/{chunk_id}/previous-raw-audio")
def previous_raw_chunk_audio(project_id: str, chunk_id: str):
    require_chunk(project_id, chunk_id)
    path = storage.PROJECTS / project_id / f"{chunk_id}.anterior.raw.wav"
    if not (storage.PROJECTS / project_id / f"{chunk_id}.anterior.wav").is_file() or not path.is_file():
        raise HTTPException(404, "La versión anterior no conserva el audio original.")
    return FileResponse(path, media_type="audio/wav", headers={"Cache-Control": "no-store"})


class DiagnosticInput(BaseModel):
    text: str = Field(min_length=1, max_length=350)
    similarity: Literal["reference", "timbre"] = "reference"


@app.post("/api/projects/{project_id}/diagnostics")
def create_diagnostic(project_id: str, payload: DiagnosticInput):
    with engine.lock:
        project = require_project(project_id)
        voice = storage.one("SELECT * FROM voices WHERE id = ?", (project["voice_id"],))
        if not voice:
            raise HTTPException(404, "La muestra de voz de este proyecto ya no existe.")
        text = payload.text.strip()
        if not text:
            raise HTTPException(400, "Escribe una frase corta para la prueba.")
        settings = settings_from_json(project["settings"]).model_copy(update={"similarity": payload.similarity})
        run_id = new_id()
        directory = storage.PROJECTS / project_id / "diagnostics" / run_id
        directory.mkdir(parents=True, exist_ok=False, mode=0o700)
        try:
            wave, sample_rate, model_size = engine.generate(
                voice["id"], storage.DATA / voice["sample_path"], voice["transcript"], text, settings
            )
            variants = {
                "raw": np.asarray(wave, dtype=np.float32),
                "rubberband": process_generated_audio(wave, sample_rate, settings.speed, False, "rubberband"),
                "atempo": process_generated_audio(wave, sample_rate, settings.speed, False, "atempo"),
                "configured": process_generated_audio(wave, sample_rate, settings.speed, settings.audio_effects, settings.speed_method),
            }
            for kind, samples in variants.items():
                path = directory / f"{kind}.wav"
                sf.write(path, samples, sample_rate, subtype="PCM_16")
                path.chmod(0o600)
            result = {
                "run_id": run_id, "text": text, "speed": settings.speed,
                "similarity": payload.similarity, "model_size": model_size,
                "audio": {kind: f"/api/projects/{project_id}/diagnostics/{run_id}/{kind}" for kind in variants},
            }
            metadata = directory / "metadata.json"
            metadata.write_text(json.dumps(result, ensure_ascii=False), encoding="utf-8")
            metadata.chmod(0o600)
            # A few recent comparisons are enough, including one for each clone mode.
            root = directory.parent
            old_runs = sorted(root.iterdir(), key=lambda path: path.stat().st_mtime, reverse=True)[4:]
            for old in old_runs:
                if old.is_dir():
                    shutil.rmtree(old)
            return result
        except ModelError as error:
            shutil.rmtree(directory, ignore_errors=True)
            raise HTTPException(503, str(error)) from error
        except (RuntimeError, ValueError) as error:
            shutil.rmtree(directory, ignore_errors=True)
            raise HTTPException(500, str(error)) from error
        except Exception:
            shutil.rmtree(directory, ignore_errors=True)
            raise


@app.get("/api/projects/{project_id}/diagnostics")
def list_diagnostics(project_id: str):
    require_project(project_id)
    root = storage.PROJECTS / project_id / "diagnostics"
    runs = []
    if root.is_dir():
        for directory in sorted(root.iterdir(), key=lambda path: path.stat().st_mtime, reverse=True):
            metadata = directory / "metadata.json"
            if directory.is_dir() and metadata.is_file():
                runs.append(json.loads(metadata.read_text(encoding="utf-8")))
    return runs


@app.get("/api/projects/{project_id}/diagnostics/latest")
def latest_diagnostic(project_id: str):
    runs = list_diagnostics(project_id)
    if runs:
        return runs[0]
    raise HTTPException(404, "Todavía no hay una prueba de calidad para este proyecto.")


@app.get("/api/projects/{project_id}/diagnostics/{run_id}/{kind}")
def diagnostic_audio(project_id: str, run_id: str, kind: Literal["raw", "rubberband", "atempo", "configured"]):
    require_project(project_id)
    if len(run_id) != 32 or any(char not in "0123456789abcdef" for char in run_id):
        raise HTTPException(404, "No encuentro esta prueba.")
    path = storage.PROJECTS / project_id / "diagnostics" / run_id / f"{kind}.wav"
    if not path.is_file():
        raise HTTPException(404, "No encuentro esta prueba.")
    return FileResponse(path, media_type="audio/wav", headers={"Cache-Control": "no-store"})


@app.post("/api/projects/{project_id}/export")
def export_project(
    project_id: str,
    format: str = Query("wav", pattern="^(wav|mp3)$"),
    version: Literal["current", "previous"] = Query("current"),
):
    with engine.lock:
        return _export_project(project_id, format, version)


def _export_project(project_id: str, format: str, version: Literal["current", "previous"]):
    project = require_project(project_id)
    chunks = storage.all_rows(
        "SELECT * FROM chunks WHERE project_id = ? ORDER BY position", (project_id,)
    )
    if not chunks:
        raise HTTPException(400, "El proyecto no tiene audio para exportar.")
    if version == "previous":
        files = [storage.PROJECTS / project_id / f"{chunk['id']}.anterior.wav" for chunk in chunks]
        if any(not path.is_file() for path in files):
            raise HTTPException(400, "Falta la versión anterior de algún fragmento. Regénéralo para poder exportarla.")
    else:
        if any(not chunk["audio_path"] for chunk in chunks):
            raise HTTPException(400, "Genera todos los fragmentos antes de exportar.")
        files = []
        for chunk in chunks:
            original = storage.PROJECTS / project_id / f"{chunk['id']}.raw.wav"
            files.append(original if original.is_file() else storage.DATA / chunk["audio_path"])
    if any(not path.is_file() for path in files):
        raise HTTPException(404, "Falta el audio de uno de los fragmentos.")
    wav = storage.EXPORTS / f"{project_id}.{version}.wav"
    try:
        combine_wav(files, wav)
        wav.chmod(0o600)
        output = wav
        if format == "mp3":
            output = storage.EXPORTS / f"{project_id}.{version}.mp3"
            wav_to_mp3(wav, output)
            output.chmod(0o600)
    except (ValueError, RuntimeError) as error:
        raise HTTPException(500, str(error)) from error
    safe_title = "".join(c if c.isalnum() or c in "-_ " else "" for c in project["title"]).strip() or "Voz Local"
    return FileResponse(
        output, media_type="audio/wav" if format == "wav" else "audio/mpeg",
        filename=f"{safe_title} - {'anterior' if version == 'previous' else 'original de Qwen'}.{format}",
        headers={"Cache-Control": "no-store"},
    )


@app.get("/api/ollama/models")
def ollama_models():
    return {"models": engine.ollama_models()}


class RewriteInput(BaseModel):
    text: str = Field(min_length=1, max_length=30000)
    instruction: str = Field(min_length=1, max_length=500)
    model: str


@app.post("/api/ollama/rewrite")
def rewrite_script(payload: RewriteInput):
    if payload.model not in engine.ollama_models():
        raise HTTPException(400, "Ese modelo no está disponible en Ollama.")
    try:
        text = engine.rewrite_script(payload.text, payload.instruction, payload.model)
    except ModelError as error:
        raise HTTPException(503, str(error)) from error
    return {"text": text}
