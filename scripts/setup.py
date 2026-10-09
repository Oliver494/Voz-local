"""First-run setup and launcher. Runs with uv-managed Python, without extra packages."""
import argparse
import os
from pathlib import Path
import platform
import shutil
import socket
import subprocess
import sys
import threading
import time
import urllib.request
import webbrowser

ROOT = Path(__file__).resolve().parent.parent
PYTHON = ROOT / '.venv' / ('Scripts/python.exe' if os.name == 'nt' else 'bin/python')
URL = 'http://127.0.0.1:8765/'


def run(args, **kwargs):
    subprocess.run([str(arg) for arg in args], cwd=ROOT, check=True, **kwargs)


def existing_server():
    with socket.socket() as sock:
        if sock.connect_ex(('127.0.0.1', 8765)) != 0:
            return False
    try:
        with urllib.request.urlopen(URL, timeout=5) as response:
            if b'Voz Local' not in response.read(8192):
                raise RuntimeError('Port 8765 is occupied by another app / El puerto 8765 esta ocupado.')
    except OSError as error:
        raise RuntimeError('Port 8765 is occupied but Voz Local did not respond / Puerto ocupado.') from error
    webbrowser.open(URL)
    print('Voz Local is already running / Voz Local ya esta encendido.', flush=True)
    return True


def environment_ready():
    if not PYTHON.exists():
        return False
    result = subprocess.run([str(PYTHON), '-c',
        "import torch, torchaudio, fastapi, uvicorn, qwen_tts, soundfile, multipart, huggingface_hub"],
        cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return result.returncode == 0


def torch_packages():
    # Keep the known working gfx1200 setup; other AMD computers use CPU by default.
    gpu_info = ''
    if sys.platform.startswith('linux'):
        for command in (['lspci'], ['/opt/rocm/bin/rocminfo']):
            try:
                result = subprocess.run(command, capture_output=True, text=True, timeout=15)
                gpu_info += result.stdout
            except (OSError, subprocess.TimeoutExpired):
                pass
        if '9060' in gpu_info or 'gfx1200' in gpu_info:
            return ['--extra-index-url', 'https://stable.repo.amd.com/rocm/whl-next/',
                    'torch[device-gfx1200]==2.12.0+rocm10.0.0', 'torchaudio==2.11.0+rocm10.0.0']
    # A driver must already be present. The installer does not replace GPU drivers.
    if shutil.which('nvidia-smi'):
        return ['--index-url', 'https://download.pytorch.org/whl/cu128',
                'torch==2.9.1', 'torchaudio==2.9.1']
    if sys.platform == 'darwin':
        if platform.machine() != 'arm64':
            raise RuntimeError('This installer requires an Apple Silicon Mac / Se necesita un Mac Apple Silicon.')
        return ['torch==2.9.1', 'torchaudio==2.9.1']
    return ['--index-url', 'https://download.pytorch.org/whl/cpu',
            'torch==2.9.1', 'torchaudio==2.9.1']


def prepare(uv):
    if not shutil.which('ffmpeg'):
        raise RuntimeError('FFmpeg is missing. Run the platform launcher / Falta FFmpeg; abre el iniciador.')
    if not environment_ready():
        if (ROOT / '.venv').exists() and not PYTHON.exists():
            raise RuntimeError('The .venv belongs to another system. Rename it and run again / Renombra .venv; no copies entornos entre equipos.')
        print('Installing project dependencies / Instalando dependencias...', flush=True)
        if not PYTHON.exists():
            run([uv, 'venv', '--python', '3.12', str(ROOT / '.venv')])
        packages = torch_packages()
        run([uv, 'pip', 'install', '--python', PYTHON, *packages])
        run([uv, 'pip', 'install', '--python', PYTHON, '-r', ROOT / 'requirements.txt'])
    run([PYTHON, '-c',
        'from app.runtime import runtime_info; import json; print(json.dumps(runtime_info(), ensure_ascii=False))'])
    print('Downloading voice model if needed / Preparando modelo de voz (puede tardar)...', flush=True)
    run([PYTHON, ROOT / 'scripts' / 'download-model.py'])
    run([PYTHON, ROOT / 'scripts' / 'package.py'])


def open_when_ready(process):
    for _ in range(120):
        if process.poll() is not None:
            return
        try:
            with urllib.request.urlopen(URL, timeout=2) as response:
                if b'Voz Local' in response.read(8192):
                    webbrowser.open(URL)
                    return
        except OSError:
            time.sleep(1)
    print(f'Open manually / Abre manualmente: {URL}', flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--uv', required=True)
    parser.add_argument('--install-only', action='store_true')
    args = parser.parse_args()
    if not args.install_only and existing_server():
        return
    os.environ.setdefault('TORCH_ROCM_AOTRITON_ENABLE_EXPERIMENTAL', '1')
    prepare(args.uv)
    if args.install_only:
        return
    print(f'Voz Local: {URL}\nKeep this window open. Ctrl+C stops the server / Mantén esta ventana abierta.', flush=True)
    process = subprocess.Popen([str(PYTHON), '-m', 'uvicorn', 'app.main:app',
                               '--host', '127.0.0.1', '--port', '8765'], cwd=ROOT)
    threading.Thread(target=open_when_ready, args=(process,), daemon=True).start()
    try:
        code = process.wait()
    except KeyboardInterrupt:
        if process.poll() is None:
            process.terminate()
        try:
            process.wait(timeout=15)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
        code = 0
    if code:
        raise RuntimeError(f'Server stopped with error {code} / El servidor fallo.')


if __name__ == '__main__':
    try:
        main()
    except (Exception, KeyboardInterrupt) as error:
        print(f'\nSetup stopped / Instalacion detenida: {error}\nCheck internet, available disk space and permissions / Revisa internet, espacio y permisos.', file=sys.stderr)
        sys.exit(1)
