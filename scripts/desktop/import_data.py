"""Import a legacy installation without modifying it; validate DB paths before commit."""
import argparse
if __name__ == "__main__":
    import lifecycle
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




def recover_import(destination):
    destination=Path(destination).resolve()
    journal=destination/'import-journal.json'
    if not journal.exists(): return
    record=json.loads(journal.read_text())
    name=record['backup']
    if not name.startswith('.before-import-') or Path(name).name != name:
        raise ValueError('Invalid import recovery journal')
    backup=destination/name
    for name in ('voices','projects','voz_local.sqlite3','desktop-settings.json'):
        saved=backup/name;target=destination/name
        if saved.exists():
            if target.is_dir():shutil.rmtree(target)
            else:target.unlink(missing_ok=True)
            os.replace(saved,target)
        elif name not in record['had_old']:
            if target.is_dir():shutil.rmtree(target)
            else:target.unlink(missing_ok=True)
    journal.unlink()
    if backup.exists() and not any(backup.iterdir()):backup.rmdir()


def import_data(source, destination):
    source, destination = Path(source).resolve(), Path(destination).resolve()
    if source == destination or source in destination.parents or destination in source.parents:
        raise ValueError('Choose a separate source data folder / Elige una carpeta de origen diferente.')
    recover_import(destination)
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
        config=destination/'desktop-settings.json'
        had_old=[name for name in ('voices','projects','voz_local.sqlite3','desktop-settings.json') if (destination/name).exists()]
        if config.exists():shutil.copy2(config,backup/'desktop-settings.json')
        journal=destination/'import-journal.json'
        with journal.open('w') as handle:
            json.dump({'backup':backup.name,'had_old':had_old},handle)
            handle.flush();os.fsync(handle.fileno())
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
            recover_import(destination)
            raise
        finally:
            if backup.exists() and not any(backup.iterdir()): backup.rmdir()
        journal.unlink(missing_ok=True)
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
        print(json.dumps({'phase':'error','message':str(error)}),flush=True)
        print(str(error), file=__import__('sys').stderr)
        raise SystemExit(1)
