"""Private environment provisioning, structured progress, resumable model downloads."""
import argparse
if __name__ == "__main__":
    import lifecycle
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import threading

PRINT_LOCK = threading.Lock()

def emit(phase, message, **extra):
    with PRINT_LOCK:
        print(json.dumps(dict(phase=phase, message=message, **extra)), flush=True)

def run(args, progress=False, **kwargs):
    if os.name == "nt": kwargs.setdefault("creationflags", subprocess.CREATE_NO_WINDOW)
    subprocess.run([str(a) for a in args], check=True, stdout=None if progress else sys.stderr, **kwargs)

def install(args):
    root = Path(args.data).resolve()
    root.mkdir(parents=True, exist_ok=True)
    resources = Path(__file__).resolve().parents[2]
    python = root / 'environment' / ('Scripts/python.exe' if os.name == 'nt' else 'bin/python')
    if shutil.disk_usage(root).free < 1024 ** 3:
        raise RuntimeError('Less than 1 GB free. Free disk space before installing / Libera espacio en disco.')
    emit('python', 'Preparing private Python environment / Preparando Python')
    if not python.exists():
        run([args.uv, 'venv', '--python', '3.12', python.parent.parent])
    requirements = resources / 'requirements.txt'
    fingerprint = hashlib.sha256(requirements.read_bytes()).hexdigest()
    marker = root / 'environment-ready.json'
    try:
        installed = json.loads(marker.read_text())
    except (OSError, ValueError):
        installed = {}
    # A failed download does not force a full reinstall of an already ready environment.
    if installed.get('requirements') != fingerprint or installed.get('profile') != args.profile:
        emit('dependencies', 'Installing PyTorch and voice dependencies / Instalando dependencias')
        packages = ['torch==2.9.1', 'torchaudio==2.9.1']
        if args.profile == 'rocm':
            packages = ['--extra-index-url', 'https://stable.repo.amd.com/rocm/whl-next/',
                        'torch[device-gfx1200]==2.12.0+rocm10.0.0', 'torchaudio==2.11.0+rocm10.0.0']
        elif args.profile == 'cuda':
            packages = ['--index-url', 'https://download.pytorch.org/whl/cu128', *packages]
        else:
            packages = ['--index-url', 'https://download.pytorch.org/whl/cpu', *packages]
        run([args.uv, 'pip', 'install', '--python', python, *packages])
        run([args.uv, 'pip', 'install', '--python', python, '-r', requirements])
    emit('device', 'Checking actual PyTorch computation / Comprobando el dispositivo')
    probe = f"""import sys, torch, json
sys.path.insert(0, {str(resources)!r})
from app.runtime import runtime_info
info = runtime_info()
device = info['device']
x = torch.ones((32,32), device=device, dtype=getattr(torch, info['dtype']))
assert float((x @ x)[0,0].cpu()) == 32.0
if device != 'cpu': torch.cuda.synchronize()
print(json.dumps(info))
"""
    result = subprocess.run([str(python), '-c', probe], capture_output=True, text=True, timeout=120, creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0)
    if result.returncode:
        raise RuntimeError('PyTorch could not run on this device. For GPU errors retry with CPU; for CPU errors check the diagnostic log. / PyTorch no funciona en este dispositivo. Si falla la GPU, reintenta con CPU; si ya usas CPU, revisa el diagnóstico.\n' + result.stderr[-2000:])
    marker.write_text(json.dumps({'requirements': fingerprint, 'profile': args.profile}))
    emit('model', 'Preparing voice model / Preparando modelo')
    env = dict(os.environ, VOZ_LOCAL_DATA_DIR=str(root), VOZ_LOCAL_DEFAULT_MODEL=args.model)
    run([python, Path(__file__).resolve(), '--download', '--data', root, '--model', args.model], env=env, progress=True)
    emit('ready', 'Motor preparado / Engine ready')

def download(args):
    from huggingface_hub import snapshot_download
    from tqdm.auto import tqdm
    root = Path(args.data)
    settings_path = root / 'desktop-settings.json'
    try:
        settings = json.loads(settings_path.read_text())
    except (OSError, ValueError):
        settings = {}
    directory = Path(settings.get('models_dir') or root / 'models') / f'Qwen3-TTS-12Hz-{args.model}-Base'
    required = ('model.safetensors', 'config.json', 'generation_config.json',
                'preprocessor_config.json', 'tokenizer_config.json', 'vocab.json', 'merges.txt',
                'speech_tokenizer/model.safetensors', 'speech_tokenizer/config.json')
    if all((directory / name).is_file() for name in required):
        emit('model', 'Using downloaded model / Reutilizando modelo descargado')
        return
    # Missing models go to the new app directory; never modify the legacy installation.
    directory = root / 'models' / f'Qwen3-TTS-12Hz-{args.model}-Base'
    class Progress(tqdm):
        def display(self, msg=None, pos=None):
            emit('model', str(self.desc or 'Downloading model / Descargando modelo'),
                 current=self.n, total=self.total or 0, unit=str(self.unit or 'files'))
    # Hugging Face resumes incomplete files; do not delete its cache on cancellation.
    snapshot_download(repo_id=f'Qwen/Qwen3-TTS-12Hz-{args.model}-Base', local_dir=directory, tqdm_class=Progress)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', required=True)
    parser.add_argument('--uv')
    parser.add_argument('--model', choices=['1.7B', '0.6B'], default='1.7B')
    parser.add_argument('--profile', choices=['cpu', 'cuda', 'rocm'], default='cpu')
    parser.add_argument('--download', action='store_true')
    try:
        args = parser.parse_args()
        download(args) if args.download else install(args)
    except Exception as error:
        emit('error', str(error))
        raise SystemExit(1)
