# Voz Local Desktop v0.2.0 — Preview (draft)

Tauri 2 / Rust desktop application for Windows x64 and Linux x64. The existing
Python/Qwen3-TTS voice generation and English/Spanish web interface are retained.

- Setup assistant downloads private Python 3.12, voice libraries and selected model.
- Authenticated private backend on a dynamic loopback port, supervised by the app.
- Native microphone recording, file import and WAV/MP3 save dialogs.
- Linux WebKit playback compatibility: a private read-only streaming gateway supports WAV metadata and seeking; Windows retains the Tauri media protocol.
- Reusable model directories and copy-based legacy library import.
- CPU, NVIDIA CUDA and the existing Linux RX 9060 XT ROCm profile.
- App data is separate from installation resources and is retained on uninstall.

These are unsigned preliminary packages. Building an installer is not validation
of microphone devices, voice quality or GPU drivers on every target. See
`docs/DESKTOP.md` for the current verification matrix and limitations. GPU drivers
are not installed automatically. Windows ARM and macOS are out of scope.

## Recorded verification

- Linux: a real native Tauri window completed UI → Rust → authenticated Python → SQLite → UI startup; unauthenticated requests returned 401 and the owned backend stopped on exit. Linux WAV metadata and seeking passed in the native player through the read-only media gateway.
- Real Qwen 1.7B generation on AMD/ROCm: 5.36 seconds of WAV audio; WAV/MP3 exports and Range playback passed; source sample unchanged.
- Fresh isolated Linux CPU runtime: managed Python and libraries installed, offline second setup reused dependencies/weights, and real 0.6B generation produced 9.68 seconds of audio with WAV/MP3 export.
- Python regression suite: 15 tests, including Linux-only parent-death cleanup; Rust: 2 guard tests. Windows skips the Linux-only process-group test.
- Windows NSIS and Linux deb/AppImage are built and tested in CI on their respective operating systems.
- Still pending manual validation: microphone permission/device behavior, perceived voice similarity, clean end-user Windows installation and NVIDIA GPU generation. Timing measurements are not performance guarantees.
