# Desktop bundled tools

The desktop installer bundles independent uv and FFmpeg executables. Python, PyTorch,
Qwen3-TTS and model weights are downloaded separately on first setup. Their upstream
licenses remain applicable. No user recordings, model weights, or Python environment
are included in the desktop build.

- uv 0.13.7: Copyright Astral Software Inc.; MIT OR Apache-2.0.
  Source: https://github.com/astral-sh/uv/tree/0.13.7
- FFmpeg n8.1.3-32-g760d10603e, **LGPL build, without GPL/nonfree components**.
  Source: https://github.com/FFmpeg/FFmpeg/tree/760d10603e
  Build recipes and dependency sources: https://github.com/BtbN/FFmpeg-Builds
  Exact binaries, source and build provenance: https://github.com/BtbN/FFmpeg-Builds/releases/tag/autobuild-2026-11-03-12-50
  Binary archives include upstream licensing notices. LGPL texts, source links and
  exact download URLs/checksums accompany the installed resources. FFmpeg runs as a
  separate, replaceable executable, not linked to Voz Local. Set VOZ_LOCAL_FFMPEG
  to use your own compatible executable. Redistributors must retain notices and
  comply with the bundled tools' license and corresponding-source obligations.
- Qwen3-TTS: https://github.com/QwenLM/Qwen3-TTS
- Tauri and Rust dependencies: see Cargo.lock and upstream crate licenses.

The app itself does not automatically grant a license to third-party weights.

Windows NSIS also redistributes the unmodified Microsoft Visual C++ Redistributable
x64 14.51.36247.0 installer from Microsoft's official download endpoint, verified by
SHA256 in tools.lock.json. Copyright Microsoft Corporation; proprietary Microsoft
redistributable license. Installation is performed by Microsoft's installer and may
request elevation. https://learn.microsoft.com/cpp/windows/latest-supported-vc-redist
