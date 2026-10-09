#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
if [ ! -x .venv/bin/python ]; then
  echo "Primero ejecuta ./instalar.sh" >&2
  exit 1
fi
echo "Voz Local: http://127.0.0.1:8765"
# gfx1200 uses AMD's experimental AOTriton kernels for PyTorch attention.
# Without this, Qwen falls back to the much slower manual implementation.
export TORCH_ROCM_AOTRITON_ENABLE_EXPERIMENTAL=1
if command -v xdg-open >/dev/null 2>&1; then
  (sleep 2; xdg-open http://127.0.0.1:8765 >/dev/null 2>&1 || true) &
fi
exec .venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8765
