# Voz Local

A local web app for voice cloning and video narration with **Qwen3-TTS**. Record or upload a voice sample, write your script, generate audio and export WAV or MP3.

The interface supports **English and Spanish**. The server runs on your own computer at `http://127.0.0.1:8765`.

> **Preview release:** the existing Ubuntu + RX 9060 XT setup has been used for voice generation. The new installers and generation on Windows, macOS and CPU have not been validated end to end on those machines. GPU drivers are not installed automatically.

## Download and start

Download **Voz-Local.zip** from this repository's **Releases**, extract the entire folder, and run the launcher for your system:

| System | Launcher | Notes |
| --- | --- | --- |
| Windows x64 | Double-click `Instalar e iniciar.bat` | Uses WinGet for FFmpeg and the Visual C++ runtime when missing. |
| Linux | `bash instalar-e-iniciar.sh` | System dependencies use apt, dnf or pacman. |
| macOS, Apple Silicon | `Instalar e iniciar.command`, or `bash instalar-e-iniciar.sh` | Uses Homebrew for FFmpeg. Intel Macs are not supported by this installer. |

The launcher prepares a private **Python 3.12** runtime and environment, installs app dependencies, downloads **Qwen3-TTS 1.7B Base**, starts the server and opens the browser. Internet is required for the initial downloads. Installation may ask for system permissions or license acceptance.

Keep the terminal window open while using the app. Press **Ctrl+C** to stop it. Run the same launcher next time; completed dependencies and model downloads are reused. Extract the complete project: the launcher needs the included `scripts` folder.

**Ollama is optional.** It edits scripts; it does not run the voice-cloning model. JavaScript, HTML and CSS run in the browser, so Node.js and Java are not required.

Read the [installation guide in Spanish](INSTALACION.md) for more details.

## How to use

1. Open **My voices**, name your voice and record or upload a clean sample. Enter the exact words spoken in the recording, including repetitions.
2. Save the voice. In **Create audio**, choose it and write your narration.
3. Continue to the project and press **Generate audio**. Long scripts can take several minutes.
4. Listen to the result and download **WAV** or **MP3**.

Full audio is the default. Advanced options include separate fragments, model selection, stability, reference similarity and language. Changes apply to newly generated audio; regenerate to hear them. The app preserves Qwen's original audio at 1.00× without speed processing.

## Models and hardware

- **Qwen3-TTS 1.7B Base:** default quality option.
- **Qwen3-TTS 0.6B Base:** lighter alternative, downloaded on first use.
- **0.6B Eco:** the same 0.6B model using timbre-only conditioning; it may sound less like the reference. It is not a third model.

The installer selects CUDA for NVIDIA when a driver is detected, the existing ROCm setup for a Linux RX 9060 XT, or CPU otherwise. Other AMD cards are not configured automatically. GPU and driver compatibility still matter. CPU generation can be very slow and requires sufficient RAM.

On Apple Silicon, CPU is the default. MPS can be requested with `VOZ_LOCAL_DEVICE=mps`, but is experimental and unverified. `VOZ_LOCAL_DEVICE=cpu` forces CPU; `VOZ_LOCAL_DEVICE=cuda` requests GPU operation explicitly.

## Local storage

Models, samples, projects and exports are stored in `data/`. Back up that folder to retain your work. The downloadable ZIP excludes personal recordings, projects, model weights and Python environments.

The server listens only on `127.0.0.1`. Internet is needed again if you select a model that has not been downloaded. Only clone voices you own or have permission to use.

Deleting a voice can also delete its linked projects; review the application's confirmation before accepting.

## Development

- Backend: Python, FastAPI, SQLite, PyTorch and FFmpeg.
- Frontend: HTML, CSS and JavaScript; no build step.
- Voice model: [official Qwen3-TTS](https://github.com/QwenLM/Qwen3-TTS).
- Optional script editing: [Ollama](https://ollama.com/).

After preparing the environment, Linux/macOS can start the server directly:

```bash
.venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8765
```

On Windows, use `.venv\Scripts\python.exe` instead. Rebuild the distribution ZIP with `python scripts/package.py`; it is written to `dist/Voz-Local.zip`.

The older `instalar.sh` script is specific to the original RX 9060 XT environment. For a new installation, use the launchers above. GPU setup references: [PyTorch](https://pytorch.org/get-started/locally/), [AMD ROCm](https://rocm.docs.amd.com/projects/ai-ecosystem/en/latest/frameworks/pytorch/install.html).

## Guía rápida en español

Descarga **Voz-Local.zip** desde **Releases**, extrae todo y abre el iniciador de tu sistema. En Windows, haz doble clic en **Instalar e iniciar.bat**; preparará Python aunque no lo tengas instalado.

En **Mis voces**, guarda una muestra con su texto exacto. En **Crear audio**, elige la voz y escribe el guion. Continúa, pulsa **Generar audio**, escucha y descarga WAV o MP3. Mantén abierta la terminal mientras usas la web.

Consulta [INSTALACION.md](INSTALACION.md) para permisos, compatibilidad y próximos inicios. Los instaladores nuevos para Windows y macOS todavía necesitan pruebas en equipos reales.
