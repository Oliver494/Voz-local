import importlib.util
import json
import os
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('legacy_import',ROOT/'scripts/desktop/import_data.py')
legacy=importlib.util.module_from_spec(spec)
spec.loader.exec_module(legacy)

class LegacyImportTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(); self.base=Path(self.temp.name)
        self.source=self.base/'old data'; self.dest=self.base/'new data'
        self.source.mkdir();self.dest.mkdir()
        with sqlite3.connect(self.source/'voz_local.sqlite3') as db:
            db.executescript('CREATE TABLE voices(id TEXT PRIMARY KEY,sample_path TEXT); CREATE TABLE projects(id TEXT PRIMARY KEY,voice_id TEXT REFERENCES voices(id)); CREATE TABLE chunks(id TEXT PRIMARY KEY,project_id TEXT REFERENCES projects(id),audio_path TEXT);')
            db.execute('INSERT INTO voices VALUES (?,?)',('a','voices/a.wav'))
            db.execute('INSERT INTO projects VALUES (?,?)',('b','a'))
            db.execute('INSERT INTO chunks VALUES (?,?,?)',('c','b','projects/b/c.wav'))
        (self.source/'voices').mkdir();(self.source/'voices/a.wav').write_bytes(b'voice')
        (self.source/'projects/b').mkdir(parents=True);(self.source/'projects/b/c.wav').write_bytes(b'audio')
        (self.source/'models').mkdir()
        (self.dest/'desktop-settings.json').write_text(json.dumps({'profile':'cpu','model':'0.6B'}))
    def tearDown(self):self.temp.cleanup()
    def test_copy_and_model_reuse_without_source_changes(self):
        before={str(p.relative_to(self.source)):p.read_bytes() for p in self.source.rglob('*') if p.is_file()}
        result=legacy.import_data(self.source,self.dest)
        self.assertTrue(result['imported']);self.assertEqual((self.dest/'voices/a.wav').read_bytes(),b'voice')
        self.assertEqual(result['models_dir'],str(self.source/'models'))
        after={str(p.relative_to(self.source)):p.read_bytes() for p in self.source.rglob('*') if p.is_file()}
        self.assertEqual(before,after)
    def test_missing_sample_does_not_install_database(self):
        (self.source/'voices/a.wav').unlink()
        with self.assertRaises(ValueError):legacy.import_data(self.source,self.dest)
        self.assertFalse((self.dest/'voz_local.sqlite3').exists())
    def test_path_traversal_rejected(self):
        with sqlite3.connect(self.source/'voz_local.sqlite3') as db:db.execute("UPDATE voices SET sample_path='../secret.wav'")
        with self.assertRaises(ValueError):legacy.import_data(self.source,self.dest)
        self.assertFalse((self.dest/'voz_local.sqlite3').exists())
    def test_nonempty_destination_preserved(self):
        legacy.import_data(self.source,self.dest)
        before=(self.dest/'voz_local.sqlite3').read_bytes()
        with self.assertRaises(ValueError):legacy.import_data(self.source,self.dest)
        self.assertEqual(before,(self.dest/'voz_local.sqlite3').read_bytes())
    def test_same_folder_rejected(self):
        with self.assertRaises(ValueError):legacy.import_data(self.source,self.source)
    def test_failed_commit_restores_destination(self):
        old=self.dest/'voices';old.mkdir();(old/'keep.txt').write_text('retained')
        real=os.replace
        def fail_config(a,b):
            if Path(b).name=='desktop-settings.json':raise OSError('disk full')
            return real(a,b)
        with patch.object(legacy.os,'replace',side_effect=fail_config):
            with self.assertRaises(OSError):legacy.import_data(self.source,self.dest)
        self.assertEqual((old/'keep.txt').read_text(),'retained')
        self.assertFalse((self.dest/'voz_local.sqlite3').exists())

class ModelLocationTests(unittest.TestCase):
    def test_external_complete_models_are_reused_and_missing_models_stay_local(self):
        import importlib
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);external=root/'old-models';data=root/'new-data';data.mkdir()
            model=external/'Qwen3-TTS-12Hz-1.7B-Base'
            for filename in ('model.safetensors','config.json','speech_tokenizer/model.safetensors','speech_tokenizer/config.json'):
                file=model/filename;file.parent.mkdir(parents=True,exist_ok=True);file.write_text('x')
            with patch.dict(os.environ,{'VOZ_LOCAL_DATA_DIR':str(data),'VOZ_LOCAL_MODELS_DIR':str(external)}):
                from app import storage
                importlib.reload(storage)
                self.assertEqual(storage.model_path('1.7B'),model)
                self.assertEqual(storage.model_path('0.6B'),data/'models/Qwen3-TTS-12Hz-0.6B-Base')
                self.assertFalse((external/'Qwen3-TTS-12Hz-0.6B-Base').exists())
            importlib.reload(storage)

if __name__=='__main__':unittest.main()
