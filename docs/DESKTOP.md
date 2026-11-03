# Voz Local Desktop 0.2.0 (preview)

## End users

Download the `.exe` (Windows x64), `.deb` or `.AppImage` (Linux x64) from the
**v0.2.0 desktop preview** release when available. This is a separate desktop app;
the web version and the v0.1.0 source ZIP remain available. No Python, Rust or
Node.js installation is required from the user.

Open Voz Local from its icon. The setup assistant lets you choose English/Spanish,
CPU/NVIDIA CUDA/Linux RX 9060 XT ROCm, and Qwen3-TTS 1.7B or 0.6B. It downloads
private Python 3.12, PyTorch, voice libraries and the selected model. The download
size is fetched from Hugging Face; dependencies require additional disk space.
GPU drivers must already be compatible. If the GPU computation check fails, choose
CPU and retry. CPU can be very slow. The assistant can reuse existing model weights
by selecting an old `models` directory before installing. Incomplete downloads are
resumed on retry; completed dependencies are retained.

The assistant does not bypass operating system prompts. Windows NSIS downloads
WebView2 if needed and runs Microsoft's Visual C++ runtime installer, which may ask
for elevation or a restart. Linux packages need WebKitGTK 4.1, GTK 3 and ALSA.
Linux compatibility is initially targeted at Ubuntu 24.04/26.04 x64. Windows ARM,
macOS and acceleration on other AMD GPUs are not advertised as supported.

## Daily use and migration

Create audio → select voice → write text → continue → generate → listen → export.
The desktop app records the default system microphone natively (up to 60 seconds).
You can also select an audio file using the system file picker. WAV/MP3 exports use
a native Save dialog and preserve the original Qwen audio at 1.00×.

Settings offers engine setup/restart, data folder, diagnostics and library import.
Import requires an empty desktop library: select the previous installation's `data`
folder. The importer validates its SQLite database and recording paths, stages a
copy, then installs it with rollback on failure. It does not delete or edit the
original. Complete old model weights are referenced in place; missing models are
downloaded into the new desktop data directory. Keep the original model folder
available while using referenced weights. Samples and generated audio are copied.

Closing while generation, setup or recording is active asks whether to wait or
exit. Exit discards uncommitted work and closes the app's own process tree. Saved
projects and previously committed audio remain. Failed generation preserves the
previous audio. A crashed engine can be restarted from the assistant.

## Data and architecture

- Tauri 2/Rust hosts the bundled HTML/CSS/JavaScript. No remote web content receives
  Tauri commands. External HTTP links open in the system browser.
- Rust controls private Python as a supervised child, using process groups on Unix
  and a kill-on-close Job Object on Windows. Python binds a free loopback port.
- A random per-session bearer token is sent through stdin and retained by Rust;
  it is not in URLs, frontend JavaScript, CLI arguments or access logs.
- JavaScript calls limited desktop commands. Rust forwards authenticated JSON and
  multipart requests. Audio uses the `voz-media` scheme with bounded Range reads;
  exported files stream to disk without base64 IPC.
- Web mode still uses its existing HTTP API and browser microphone/exports.
- Application data uses Tauri's local data directory (`com.oliver494.vozlocal`),
  separately from read-only program resources. It contains `environment/`,
  `python/`, `models/`, SQLite, voices, projects, logs and temporary recordings.
  Updates/uninstall do not delete that data directory.
- Python recognizes `VOZ_LOCAL_DATA_DIR`, `VOZ_LOCAL_MODELS_DIR`,
  `VOZ_LOCAL_FFMPEG` and `VOZ_LOCAL_DEFAULT_MODEL`. Without these, web defaults stay
  unchanged. The new transport does not change the TTS generation settings.
- Logs are local. Diagnostics are displayed only on request and are not uploaded.

## Building

Development requires Node.js 22, Rust stable, Python for resource preparation,
and system Tauri/CPAL build libraries. Linux/Ubuntu:

```bash
sudo apt install build-essential pkg-config libwebkit2gtk-4.1-dev libgtk-3-dev libasound2-dev librsvg2-dev patchelf
npm ci
python3 scripts/desktop/prepare_resources.py
npm run desktop:dev
```

Windows requires the normal Tauri MSVC build tools. Resource preparation on Windows:
`python scripts/desktop/prepare_resources.py --platform windows`.

Build: `npm run desktop:build -- --bundles deb,appimage` on Linux, or
`npm run desktop:build -- --bundles nsis` on Windows. Bundled uv/FFmpeg/VC runtime
versions and SHA256 checksums are locked in `scripts/desktop/tools.lock.json`.
Resource preparation verifies hashes before extracting; third-party notices and
licenses ship inside resources. See [THIRD_PARTY_NOTICES.md](../THIRD_PARTY_NOTICES.md).

GitHub Actions builds on Ubuntu 24.04 and Windows, runs regressions, uploads
installers and creates/updates a **draft prerelease** v0.2.0 only when both builds
succeed. Packages are unsigned. No automatic updater is enabled in this preview.

## Verification matrix

| Scenario | Current evidence |
| --- | --- |
| Rust/Tauri Linux compilation | `cargo check` succeeds on this Ubuntu host |
| Python API regression | 13 tests: session auth, web compatibility, invalid audio, generation failure preservation, WAV/MP3 export, Range playback, legacy import rollback/path validation and external model reuse |
| Native Rust guards | Test suite covers API path restrictions and active-operation accounting |
| Windows/Linux installers | GitHub Actions builds each on its own OS; build results are recorded in the draft release |
| Real GPU voice generation | Tested with 1.7B on this Linux AMD/ROCm host: 5.36-second original WAV, WAV/MP3 exports, authenticated sidecar and HTTP Range; sample file unchanged. Generation took 55.66 seconds including model load. Perceived voice quality still requires listening. |
| Actual microphone, perceived voice quality, clean-machine installation, crash recovery on every GPU | Requires manual validation; a successful package build does not establish these |

Before publishing a stable release, install on clean Windows/Linux machines, test
microphone denial and native save dialogs, run a real narration on each advertised
GPU profile, interrupt a model download, restart, close during generation, and
compare the voice with the web version using the same reference/settings.

## Español

La aplicación se abre desde su icono y prepara el motor con un asistente, sin
terminal. Puedes reutilizar modelos descargados e importar una biblioteca anterior
sin modificarla. No se instalan controladores de GPU. Si falla la comprobación de
PyTorch, elige CPU. Los paquetes son preliminares y sin firma; una compilación
correcta no garantiza todavía todas las tarjetas, micrófonos ni equipos.
