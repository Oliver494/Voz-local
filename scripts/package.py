"""Build a source ZIP without environments, model weights or personal recordings."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

root = Path(__file__).resolve().parent.parent
files = [root / name for name in (
    'README.md', 'INSTALACION.md', 'requirements.txt',
    'Instalar e iniciar.bat', 'Instalar e iniciar.command',
    'instalar-e-iniciar.sh', 'iniciar.sh', 'instalar.sh', '.gitignore')]
files += list((root / 'app').glob('*.py'))
files += list((root / 'scripts').glob('*.py'))
files += list((root / 'scripts').glob('*.ps1'))
files += [root / 'static' / name for name in ('index.html', 'styles.css', 'app.js')]
output = root / 'dist' / 'Voz-Local.zip'
output.parent.mkdir(exist_ok=True)
temporary = output.with_suffix('.zip.tmp')
with ZipFile(temporary, 'w', compression=ZIP_DEFLATED) as archive:
    for file in sorted(files):
        archive.write(file, arcname=str(Path('Voz Local') / file.relative_to(root)))
temporary.replace(output)
print(output)
