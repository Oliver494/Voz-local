import gc
import logging
from pathlib import Path
import re
import threading

import httpx

from .storage import MODELS
from .voice_settings import VoiceSettings
from .runtime import runtime_info


LOG = logging.getLogger(__name__)
OLLAMA_URL = "http://127.0.0.1:11434"
MODEL_IDS = {
    "1.7B": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
    "0.6B": "Qwen/Qwen3-TTS-12Hz-0.6B-Base",
}


class ModelError(Exception):
    pass


class VoiceEngine:
    def __init__(self) -> None:
        self.lock = threading.RLock()
        self.model = None
        self.active_size: str | None = None
        self.preferred_size = "1.7B"
        self.prompt_cache: dict[tuple[str, str, str], object] = {}

    def _release_locked(self) -> None:
        self.model = None
        self.active_size = None
        self.prompt_cache.clear()
        gc.collect()
        try:
            import torch
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        except Exception:
            LOG.exception("No se pudo vaciar la caché de la GPU")

    def _load_locked(self, size: str) -> None:
        if self.model is not None and self.active_size == size:
            return
        self._release_locked()
        import torch
        from huggingface_hub import snapshot_download
        from qwen_tts import Qwen3TTSModel

        model_id = MODEL_IDS[size]
        local_path = MODELS / model_id.rsplit("/", 1)[1]
        if not (local_path / "model.safetensors").is_file():
            LOG.info("Descargando %s en %s", model_id, local_path)
            snapshot_download(repo_id=model_id, local_dir=local_path)
        runtime = runtime_info()
        LOG.info("Cargando %s en %s (%s)", model_id, runtime['device'], runtime['dtype'])
        self.model = Qwen3TTSModel.from_pretrained(
            str(local_path),
            device_map=runtime['device'],
            dtype=getattr(torch, runtime['dtype']),
            attn_implementation="sdpa",
        )
        self.active_size = size

    @staticmethod
    def _out_of_memory(error: Exception) -> bool:
        message = str(error).lower()
        return "out of memory" in message or "memory allocation" in message

    def generate(self, voice_id: str, reference: Path, transcript: str, text: str, settings: VoiceSettings):
        with self.lock:
            target = "1.7B" if settings.model == "qwen-1.7b" else "0.6B"
            try:
                return self._generate_locked(target, voice_id, reference, transcript, text, settings)
            except Exception as error:
                if not self._out_of_memory(error):
                    LOG.exception("Falló la generación de audio")
                    raise ModelError(f"No se pudo generar el audio: {error}") from error
                LOG.warning("Memoria GPU insuficiente para %s; se intentará 0.6B", target)
                self._release_locked()
                if target == "0.6B":
                    raise ModelError(
                        "No hay suficiente memoria de GPU. Cierra otros modelos de Ollama y vuelve a intentarlo."
                    ) from error
                try:
                    result = self._generate_locked("0.6B", voice_id, reference, transcript, text, settings)
                    self.preferred_size = "0.6B"
                    return result
                except Exception as fallback_error:
                    self._release_locked()
                    LOG.exception("También falló el modelo de respaldo")
                    raise ModelError(
                        "Tampoco pudo iniciarse el modelo 0.6B. Libera memoria de GPU y vuelve a intentarlo."
                    ) from fallback_error

    def _generate_locked(self, size: str, voice_id: str, reference: Path, transcript: str, text: str, settings: VoiceSettings):
        self._load_locked(size)
        # Qwen defaults to a simulated streaming text layout and allows up to
        # 4096 generated tokens. On ROCm that can keep short phrases running
        # for several minutes when the model does not emit EOS promptly.
        # The web always sends complete text, so use the normal non-streaming
        # layout and cap output generously according to the amount of text.
        words = max(1, len(re.findall(r"\w+", text, flags=re.UNICODE)))
        max_new_tokens = min(2048, max(192, words * 18 + 128))
        similarity = "timbre" if settings.model == "qwen-0.6b-eco" else settings.similarity
        cache_key = (size, voice_id, similarity)
        prompt = self.prompt_cache.get(cache_key)
        if prompt is None:
            prompt = self.model.create_voice_clone_prompt(
                ref_audio=str(reference), ref_text=transcript,
                x_vector_only_mode=similarity == "timbre",
            )
            self.prompt_cache[cache_key] = prompt
        waves, sample_rate = self.model.generate_voice_clone(
            text=text,
            language=settings.language if settings.language_override else "Spanish",
            voice_clone_prompt=prompt,
            # Short reference clips avoid the rushed pacing of long ICL prompts
            # while keeping the model's original voice-cloning layout.
            non_streaming_mode=True,
            max_new_tokens=max_new_tokens,
            do_sample=True,
            top_k=50,
            top_p=1.0,
            repetition_penalty=1.05,
            temperature=round(0.93 - settings.stability * 0.0006, 3),
            subtalker_temperature=round(0.9 + settings.style * 0.001, 3),
        )
        wave = waves[0]
        if similarity == "reference" and self._output_is_too_short(wave, sample_rate, text):
            LOG.warning(
                "La generación ICL de la voz %s terminó demasiado pronto; reintentando solo con el timbre",
                voice_id,
            )
            fallback_key = (size, voice_id, "timbre")
            fallback_prompt = self.prompt_cache.get(fallback_key)
            if fallback_prompt is None:
                fallback_prompt = self.model.create_voice_clone_prompt(
                    ref_audio=str(reference), ref_text=None, x_vector_only_mode=True,
                )
                self.prompt_cache[fallback_key] = fallback_prompt
            fallback_waves, fallback_rate = self.model.generate_voice_clone(
                text=text,
                language=settings.language if settings.language_override else "Spanish",
                voice_clone_prompt=fallback_prompt,
                non_streaming_mode=True,
                max_new_tokens=max_new_tokens,
                do_sample=True,
                top_k=50,
                top_p=1.0,
                repetition_penalty=1.05,
                temperature=round(0.93 - settings.stability * 0.0006, 3),
                subtalker_temperature=round(0.9 + settings.style * 0.001, 3),
            )
            wave, sample_rate = fallback_waves[0], fallback_rate
        if self._output_is_too_short(wave, sample_rate, text):
            raise ModelError(
                "Qwen terminó el audio demasiado pronto. Comprueba que el texto de la muestra "
                "coincida palabra por palabra con lo que se oye y vuelve a intentarlo."
            )
        return wave, sample_rate, "0.6B Eco" if settings.model == "qwen-0.6b-eco" else size

    @staticmethod
    def _output_is_too_short(wave, sample_rate: int, text: str) -> bool:
        """Detecta salidas truncadas sin rechazar frases cortas dichas con rapidez."""
        duration = len(wave) / sample_rate if sample_rate else 0
        words = len(re.findall(r"\w+", text, flags=re.UNICODE))
        minimum = max(0.45, words / 7.5)
        return duration < minimum

    def ollama_models(self) -> list[str]:
        try:
            response = httpx.get(f"{OLLAMA_URL}/api/tags", timeout=3)
            response.raise_for_status()
            return [item["name"] for item in response.json().get("models", [])]
        except (httpx.HTTPError, ValueError, KeyError):
            return []

    def rewrite_script(self, text: str, instruction: str, model: str) -> str:
        with self.lock:
            self._release_locked()
            try:
                with httpx.Client(timeout=180) as client:
                    response = client.post(
                        f"{OLLAMA_URL}/api/chat",
                        json={
                            "model": model,
                            "messages": [
                                {"role": "system", "content": "Eres un editor de guiones en español. Devuelve solo el guion final, sin notas ni explicaciones. Conserva los hechos y el sentido del texto original."},
                                {"role": "user", "content": f"Instrucción: {instruction}\n\nGuion:\n{text}"},
                            ],
                            "stream": False,
                            "keep_alive": 0,
                        },
                    )
                    response.raise_for_status()
                    rewritten = response.json().get("message", {}).get("content", "").strip()
                    if not rewritten:
                        raise ModelError("Ollama devolvió una respuesta vacía.")
                    return rewritten
            except httpx.HTTPError as error:
                raise ModelError("No se pudo conectar con Ollama o terminó con un error.") from error
            finally:
                try:
                    httpx.post(
                        f"{OLLAMA_URL}/api/chat",
                        json={"model": model, "messages": [], "keep_alive": 0},
                        timeout=5,
                    )
                except httpx.HTTPError:
                    pass


engine = VoiceEngine()
