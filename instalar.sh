#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

if ! command -v ffmpeg >/dev/null 2>&1; then
  echo "Falta FFmpeg. Instálalo con: sudo apt install ffmpeg" >&2
  exit 1
fi

python3 -m venv .installer
.installer/bin/python -m pip install --disable-pip-version-check uv
.installer/bin/uv python install 3.12
.installer/bin/uv venv --python 3.12 .venv
.installer/bin/uv pip install --python .venv/bin/python pip
.venv/bin/python -m pip install --disable-pip-version-check \
  --extra-index-url https://stable.repo.amd.com/rocm/whl-next/ \
  'torch[device-gfx1200]==2.12.0+rocm10.0.0' \
  'torchaudio==2.11.0+rocm10.0.0'
.venv/bin/python -m pip install --disable-pip-version-check -r requirements.txt
.venv/bin/python - <<'PY'
from huggingface_hub import snapshot_download
snapshot_download(
    repo_id="Qwen/Qwen3-TTS-12Hz-1.7B-Base",
    local_dir="data/models/Qwen3-TTS-12Hz-1.7B-Base",
)
PY
echo "Instalación terminada. Ejecuta ./iniciar.sh"
