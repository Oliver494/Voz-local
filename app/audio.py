from pathlib import Path
import re
import subprocess
import wave
import numpy as np

import soundfile as sf


def split_script(script: str, target: int = 220, maximum: int = 350) -> list[str]:
    normalized = re.sub(r"[ \t]+", " ", script.strip())
    sentences = re.split(r"(?<=[.!?…])\s+|\n+", normalized)
    parts: list[str] = []
    current = ""
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
        words = sentence.split()
        small_parts: list[str] = []
        small = ""
        for word in words:
            candidate = f"{small} {word}".strip()
            if len(candidate) > maximum and small:
                small_parts.append(small)
                small = word
            else:
                small = candidate
        if small:
            small_parts.append(small)
        for item in small_parts:
            candidate = f"{current} {item}".strip()
            if current and len(candidate) > target:
                parts.append(current)
                current = item
            else:
                current = candidate
    if current:
        parts.append(current)
    return parts


def normalize_reference(source: Path, destination: Path) -> float:
    command = [
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-nostdin", "-y",
        "-i", str(source), "-vn", "-ac", "1", "-ar", "24000",
        "-c:a", "pcm_s16le", str(destination),
    ]
    result = subprocess.run(command, capture_output=True, text=True, timeout=90)
    if result.returncode:
        raise ValueError("No pude leer el audio. Sube WAV, MP3, M4A u otro formato de audio válido.")
    info = sf.info(destination)
    if not 3 <= info.duration <= 30:
        raise ValueError("La muestra debe durar entre 3 y 30 segundos.")
    return info.duration


def process_generated_audio(samples, sample_rate: int, speed: float, effects: bool, method: str = "rubberband"):
    if speed == 1.0 and not effects:
        return samples
    filters = []
    if speed != 1.0:
        if method == "atempo":
            # FFmpeg skips samples above 2x in a single atempo filter.
            factor = speed ** 0.5 if speed > 2 else speed
            filters.extend([f"atempo={factor:.6f}"] * (2 if speed > 2 else 1))
        elif method == "rubberband":
            filters.append(f"rubberband=tempo={speed:.3f}:pitch=1:formant=preserved:transients=smooth:window=long")
        else:
            raise ValueError("Método de velocidad desconocido.")
    if effects:
        filters.extend(("highpass=f=70", "acompressor=threshold=0.125:ratio=2:attack=12:release=100:makeup=1"))
    result = subprocess.run(
        ["ffmpeg", "-hide_banner", "-loglevel", "error", "-nostdin", "-f", "f32le",
         "-ar", str(sample_rate), "-ac", "1", "-i", "pipe:0", "-af", ",".join(filters),
         "-f", "f32le", "-ac", "1", "-ar", str(sample_rate), "pipe:1"],
        input=np.asarray(samples, dtype="<f4").tobytes(), capture_output=True, timeout=180,
    )
    if result.returncode or not result.stdout:
        raise RuntimeError("No se pudieron aplicar los ajustes de audio. Desactiva los efectos e inténtalo de nuevo.")
    return np.frombuffer(result.stdout, dtype="<f4").copy()


def combine_wav(files: list[Path], destination: Path) -> None:
    if not files:
        raise ValueError("No hay fragmentos para exportar.")
    with wave.open(str(files[0]), "rb") as first:
        parameters = first.getparams()
    with wave.open(str(destination), "wb") as output:
        output.setnchannels(parameters.nchannels)
        output.setsampwidth(parameters.sampwidth)
        output.setframerate(parameters.framerate)
        for path in files:
            with wave.open(str(path), "rb") as fragment:
                if (
                    fragment.getnchannels() != parameters.nchannels
                    or fragment.getsampwidth() != parameters.sampwidth
                    or fragment.getframerate() != parameters.framerate
                ):
                    raise ValueError("Los fragmentos tienen formatos de audio incompatibles.")
                while frames := fragment.readframes(65536):
                    output.writeframes(frames)


def wav_to_mp3(source: Path, destination: Path) -> None:
    result = subprocess.run(
        ["ffmpeg", "-hide_banner", "-loglevel", "error", "-nostdin", "-y",
         "-i", str(source), "-codec:a", "libmp3lame", "-b:a", "192k", str(destination)],
        capture_output=True, text=True, timeout=180,
    )
    if result.returncode:
        raise RuntimeError("No se pudo convertir el audio a MP3.")
