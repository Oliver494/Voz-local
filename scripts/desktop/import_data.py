"""Import a legacy installation without modifying it; validate DB paths before commit."""
import argparse
import json
import os
from pathlib import Path
import shutil
import sqlite3
import uuid

from contextlib import contextmanager

@contextmanager
def closed_connection(*args, **kwargs):
    db = sqlite3.connect(*args, **kwargs)
    try:
        with db:
            yield db
    finally:
        db.close()



def import_data(source, destination):
    source, destination = Path(source).resolve(), Path(destination).resolve()
    if source == destination or source in destination.parents or destination in source.parents:
        raise ValueError('Choose a separate source data folder / Elige una carpeta de origen diferente.')
    database = destination / 'voz_local.sqlite3'
    if database.exists():
        with closed_connection(database) as db:
            if db.execute('select count(*) from voices').fetchone()[0] or db.execute('select count(*) from projects').fetchone()[0]:
                raise ValueError('Import requires an empty desktop library / La biblioteca de destino debe estar vacía.')
    stage = destination / ('.import-' + uuid.uuid4().hex)
    stage.mkdir(parents=True)
    try:
        uri = (source / 'voz_local.sqlite3').as_uri() + '?mode=ro'
        with closed_connection(uri, uri=True) as original, closed_connection(stage / 'voz_local.sqlite3') as copied:
            original.backup(copied)
            if copied.execute('PRAGMA integrity_check').fetchone()[0] != 'ok':
                raise ValueError('Database is damaged / Base de datos dañada.')
            tables = {row[0] for row in copied.execute("select name from sqlite_master where type='table'")}
            if not {'voices', 'projects', 'chunks'} <= tables:
                raise ValueError('This is not a Voz Local database.')
            if copied.execute('PRAGMA foreign_key_check').fetchone():
                raise ValueError('Broken project references / Referencias de proyecto incompletas.')
            refs = [('voices', row[0]) for row in copied.execute('select sample_path from voices')]
            refs += [('projects', row[0]) for row in copied.execute('select audio_path from chunks where audio_path is not null')]
            for kind, value in refs:
                relative = Path(value.replace('\\', '/'))
                target = (source / relative).resolve()
                if relative.is_absolute() or target == source or source not in target.parents or relative.parts[0] != kind or not target.is_file():
                    raise ValueError(f'Invalid or missing recording / Falta una grabación: {relative}')
                copied_path = stage / relative
                copied_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(target, copied_path)
            # Normalize Windows separators so archives can be imported on Linux too.
            copied.execute("update voices set sample_path=replace(sample_path, char(92), '/')")
            copied.execute("update chunks set audio_path=replace(audio_path, char(92), '/') where audio_path is not null")
        # Preserve additional original WAV variants (without following symlinks).
        for folder in ('voices', 'projects'):
            if (source / folder).is_dir():
                for file in (source / folder).rglob('*'):
                    if file.is_file() and not file.is_symlink() and source in file.resolve().parents:
                        target = stage / file.relative_to(source)
                        target.parent.mkdir(parents=True, exist_ok=True)
                        if not target.exists(): shutil.copy2(file, target)
        # Stage completely before installing. Roll back destination on interrupted commit.
        backup = destination / ('.before-import-' + uuid.uuid4().hex)
        backup.mkdir()
        installed = []
        moved = []
        try:
            for name in ('voices', 'projects', 'voz_local.sqlite3'):
                old = destination / name
                if old.exists():
                    os.replace(old, backup / name)
                    moved.append(name)
                new = stage / name
                if new.exists():
                    os.replace(new, old)
                    installed.append(name)
            config = destination / 'desktop-settings.json'
            settings = json.loads(config.read_text()) if config.exists() else {}
            if (source / 'models').is_dir(): settings['models_dir'] = str(source / 'models')
            temporary = config.with_suffix('.tmp')
            temporary.write_text(json.dumps(settings))
            os.replace(temporary, config)
        except BaseException:
            for name in installed:
                target = destination / name
                shutil.rmtree(target) if target.is_dir() else target.unlink(missing_ok=True)
            for name in moved: os.replace(backup / name, destination / name)
            raise
        finally:
            if backup.exists() and not any(backup.iterdir()): backup.rmdir()
        # Keep the previous empty DB backup until the next import; never touch source.
        return {'imported': True, 'models_dir': settings.get('models_dir')}
    finally:
        shutil.rmtree(stage, ignore_errors=True)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('source')
    parser.add_argument('destination')
    args = parser.parse_args()
    try: print(json.dumps(import_data(args.source, args.destination)))
    except Exception as error:
        print(str(error), file=__import__('sys').stderr)
        raise SystemExit(1)
