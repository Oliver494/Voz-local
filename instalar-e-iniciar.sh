#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
trap 'echo "No se pudo completar. Revisa el mensaje anterior y vuelve a ejecutar este archivo." >&2' ERR

if ! command -v ffmpeg >/dev/null 2>&1 || { ! command -v curl >/dev/null 2>&1 && ! command -v wget >/dev/null 2>&1; }; then
  echo "Falta FFmpeg. Instalando las herramientas de audio..."
  if [[ "$(uname -s)" == Darwin ]]; then
    if ! command -v brew >/dev/null 2>&1; then
      echo "Preparando Homebrew desde su fuente oficial. Puede pedir permisos del sistema."
      /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
      if [[ -x /opt/homebrew/bin/brew ]]; then
        eval "$(/opt/homebrew/bin/brew shellenv)"
      elif [[ -x /usr/local/bin/brew ]]; then
        eval "$(/usr/local/bin/brew shellenv)"
      fi
    fi
    brew install ffmpeg
  elif command -v apt-get >/dev/null 2>&1; then
    sudo apt-get update
    sudo apt-get install -y ffmpeg ca-certificates curl
  elif command -v dnf >/dev/null 2>&1; then
    sudo dnf install -y ffmpeg-free curl ca-certificates
  elif command -v pacman >/dev/null 2>&1; then
    sudo pacman -S --needed ffmpeg curl ca-certificates
  else
    echo "Instala FFmpeg con el gestor de tu sistema y vuelve a abrir este archivo." >&2
    exit 1
  fi
fi

mkdir -p .runtime
if [[ ! -x .runtime/bin/uv ]]; then
  echo "Preparando el instalador de Python..."
  if command -v curl >/dev/null 2>&1; then
    curl -fsSL https://astral.sh/uv/install.sh -o .runtime/uv-install.sh
  elif command -v wget >/dev/null 2>&1; then
    wget -O .runtime/uv-install.sh https://astral.sh/uv/install.sh
  else
    echo "Instala curl o wget y vuelve a abrir este archivo." >&2
    exit 1
  fi
  UV_INSTALL_DIR="$PWD/.runtime/bin" UV_NO_MODIFY_PATH=1 sh .runtime/uv-install.sh
fi
export UV_PYTHON_INSTALL_DIR="$PWD/.runtime/python"
export UV_PYTHON_PREFERENCE=only-managed
.runtime/bin/uv python install 3.12
exec .runtime/bin/uv run --no-project --python 3.12 scripts/setup.py --uv "$PWD/.runtime/bin/uv"
