# Voz Local Desktop v0.2.0 — Preview (draft)

Tauri 2 / Rust desktop application for Windows x64 and Linux x64. The existing
Python/Qwen3-TTS voice generation and English/Spanish web interface are retained.

- Setup assistant downloads private Python 3.12, voice libraries and selected model.
- Authenticated private backend on a dynamic loopback port, supervised by the app.
- Native microphone recording, file import and WAV/MP3 save dialogs.
- Reusable model directories and copy-based legacy library import.
- CPU, NVIDIA CUDA and the existing Linux RX 9060 XT ROCm profile.
- App data is separate from installation resources and is retained on uninstall.

These are unsigned preliminary packages. Building an installer is not validation
of microphone devices, voice quality or GPU drivers on every target. See
`docs/DESKTOP.md` for the current verification matrix and limitations. GPU drivers
are not installed automatically. Windows ARM and macOS are out of scope.
