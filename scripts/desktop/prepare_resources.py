"""Build-time resources only. Pinned, SHA256-verified tools, never private data."""
import argparse
import hashlib
import io
import json
from pathlib import Path
import shutil
import struct
import sys
import tarfile
import urllib.request
import zipfile
import zlib

ROOT = Path(__file__).resolve().parents[2]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--platform', choices=['windows','linux'], default='windows' if sys.platform == 'win32' else 'linux')
    args = parser.parse_args()
    target = ROOT / 'src-tauri/resources'
    target.mkdir(parents=True, exist_ok=True)
    lock = json.loads(Path(__file__).with_name('tools.lock.json').read_text())
    cache = ROOT / '.build-deps/downloads'
    cache.mkdir(parents=True, exist_ok=True)
    suffix = '.exe' if args.platform == 'windows' else ''
    tools = target / 'tools'
    tools.mkdir(exist_ok=True)
    notices = target / 'licenses'
    notices.mkdir(exist_ok=True)
    for name, spec in lock[args.platform].items():
        archive = cache / spec['url'].split('/')[-1]
        if not archive.exists() or hashlib.sha256(archive.read_bytes()).hexdigest() != spec['sha256']:
            temporary = archive.with_suffix('.download')
            print('Downloading pinned build resource:', name, flush=True)
            urllib.request.urlretrieve(spec['url'], temporary)
            if hashlib.sha256(temporary.read_bytes()).hexdigest() != spec['sha256']:
                temporary.unlink()
                raise RuntimeError('SHA256 mismatch: ' + name)
            temporary.replace(archive)
        if name == "vcredist":
            shutil.copy2(archive, tools / "vc_redist.x64.exe")
            continue
        executable = name + suffix
        found = False
        license_dir = notices / name
        license_dir.mkdir(exist_ok=True)
        if zipfile.is_zipfile(archive):
            with zipfile.ZipFile(archive) as bundle:
                for item in bundle.infolist():
                    if Path(item.filename).name == executable:
                        (tools / executable).write_bytes(bundle.read(item)); found = True
                    elif not item.is_dir() and any(word in Path(item.filename).name.lower() for word in ('license','copying','readme','sources')):
                        (license_dir / Path(item.filename).name).write_bytes(bundle.read(item))
        else:
            with tarfile.open(archive) as bundle:
                for item in bundle:
                    if not item.isfile(): continue
                    if Path(item.name).name == executable:
                        (tools / executable).write_bytes(bundle.extractfile(item).read()); found = True
                    elif any(word in Path(item.name).name.lower() for word in ('license','copying','readme','sources')):
                        (license_dir / Path(item.name).name).write_bytes(bundle.extractfile(item).read())
        if not found: raise RuntimeError('Executable missing in archive: ' + executable)
        (tools / executable).chmod(0o755)
    # Include upstream license texts if binary archives omit them.
    for name, url in {
        'uv-MIT.txt':'https://raw.githubusercontent.com/astral-sh/uv/0.13.7/LICENSE-MIT',
        'uv-Apache.txt':'https://raw.githubusercontent.com/astral-sh/uv/0.13.7/LICENSE-APACHE',
        'FFmpeg-LGPL-2.1.txt':'https://raw.githubusercontent.com/FFmpeg/FFmpeg/n8.1.3/COPYING.LGPLv2.1',
        'FFmpeg-LGPL-3.txt':'https://raw.githubusercontent.com/FFmpeg/FFmpeg/n8.1.3/COPYING.LGPLv3',
    }.items():
        if not (notices / name).exists(): urllib.request.urlretrieve(url, notices / name)
    shutil.copy2(ROOT / 'THIRD_PARTY_NOTICES.md', notices)
    shutil.copy2(Path(__file__).with_name('tools.lock.json'), notices)
    backend = target / 'backend'
    for folder in ('app','static','scripts/desktop'):
        destination = backend / folder
        destination.mkdir(parents=True, exist_ok=True)
        for source in (ROOT / folder).iterdir():
            if source.is_file() and source.suffix in ('.py','.js','.html','.css','.json'):
                shutil.copy2(source, destination / source.name)
    shutil.copy2(ROOT / 'requirements.txt', backend / 'requirements.txt')
    # Code-native application icon: three white waveform bars on a dark tile.
    icons = ROOT / 'src-tauri/icons'
    icons.mkdir(exist_ok=True)
    def png(n):
        pixels = bytearray()
        for y in range(n):
            pixels.append(0)
            for x in range(n):
                wave = any(abs(x/n-cx)<.035 and abs(y/n-.5)<height for cx,height in ((.34,.14),(.5,.28),(.66,.20)))
                pixels.extend((255,255,255,255) if wave else (34,34,38,255))
        def chunk(kind, data): return struct.pack('>I',len(data))+kind+data+struct.pack('>I',zlib.crc32(kind+data)&0xffffffff)
        return b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',n,n,8,6,0,0,0))+chunk(b'IDAT',zlib.compress(pixels))+chunk(b'IEND',b'')
    for size in (32,128): (icons/f'{size}x{size}.png').write_bytes(png(size))
    image = png(128)
    (icons/'icon.ico').write_bytes(struct.pack('<HHH',0,1,1)+struct.pack('<BBBBHHII',128,128,0,0,1,32,len(image),22)+image)
    print('Desktop resources ready:', target)

if __name__ == '__main__': main()
