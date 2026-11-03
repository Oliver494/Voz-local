"""API and data regression tests with synthetic samples; no model download or GPU."""
import importlib
import io
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

class DesktopApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            import numpy, soundfile, fastapi, httpx
        except ImportError:
            raise unittest.SkipTest('API test dependencies not installed')
        cls.temp=tempfile.TemporaryDirectory();cls.root=Path(cls.temp.name)
        cls.env=patch.dict(os.environ,{'VOZ_LOCAL_DATA_DIR':str(cls.root),'VOZ_LOCAL_SESSION_TOKEN':'private-test-session-token','VOZ_LOCAL_DEFAULT_MODEL':'0.6B'})
        cls.env.start()
        from app import storage
        importlib.reload(storage)
        from app import main
        importlib.reload(main)
        cls.main=main;cls.storage=storage
        from fastapi.testclient import TestClient
        cls.client=TestClient(main.app,headers={'Authorization':'Bearer private-test-session-token'})
        cls.client.__enter__()
    @classmethod
    def tearDownClass(cls):
        cls.client.__exit__(None,None,None);cls.env.stop();cls.temp.cleanup()
    def test_requires_token_for_audio_and_json(self):
        for path in ('/api/voices','/api/projects','/api/status'):
            self.assertEqual(self.client.get(path,headers={'Authorization':''}).status_code,401)
        self.assertEqual(self.client.get('/api/voices').status_code,200)
    def test_web_mode_preserved(self):
        with patch.dict(os.environ,{},clear=False):
            token=os.environ.pop('VOZ_LOCAL_SESSION_TOKEN')
            try:self.assertEqual(self.client.get('/api/voices',headers={'Authorization':''}).status_code,200)
            finally:os.environ['VOZ_LOCAL_SESSION_TOKEN']=token
    def test_foreign_origin_rejected(self):
        self.assertEqual(self.client.post('/api/projects',headers={'Origin':'https://untrusted.example'},json={}).status_code,403)
    def test_invalid_audio_and_absent_transcript_are_errors(self):
        response=self.client.post('/api/voices',data={'name':'Broken','transcript':'hello'},files={'file':('bad.wav',b'not audio','audio/wav')})
        self.assertIn(response.status_code,(400,422))
        response=self.client.post('/api/voices',data={'name':'No text','transcript':''},files={'file':('bad.wav',b'not audio','audio/wav')})
        self.assertIn(response.status_code,(400,422))
    def test_project_audio_export_and_atomic_failure(self):
        import numpy as np
        import soundfile as sf
        from app.engine import ModelError
        identifier='a'*32;voice=self.root/'voices'/f'{identifier}.wav'
        sf.write(voice,np.zeros(24000,dtype=np.float32),24000)
        with self.storage.connection() as db:
            db.execute('INSERT OR IGNORE INTO voices(id,name,transcript,sample_path,duration) VALUES (?,?,?,?,?)',(identifier,'Synthetic test','Hello','voices/'+voice.name,1.0))
        response=self.client.post('/api/projects',json={'title':'Desktop regression','voice_id':identifier,'script':'Hello, this is a test.','mode':'continuous','voice_model':'qwen-0.6b'})
        self.assertEqual(response.status_code,200,response.text)
        project=response.json();chunk=project['chunks'][0];path=f"/api/projects/{project['id']}/chunks/{chunk['id']}/generate"
        with patch.object(self.main.engine,'generate',return_value=(np.full(2400,0.1,dtype=np.float32),24000,'0.6B')):
            generated=self.client.post(path)
        self.assertEqual(generated.status_code,200,generated.text)
        url=generated.json()['audio_url'];before=self.client.get(url).content
        ranged=self.client.get(url,headers={'Range':'bytes=0-43'})
        self.assertEqual(ranged.status_code,206);self.assertEqual(len(ranged.content),44)
        with patch.object(self.main.engine,'generate',side_effect=ModelError('GPU memory exhausted')):
            failed=self.client.post(path)
        self.assertEqual(failed.status_code,503);self.assertEqual(self.client.get(url).content,before)
        exported=self.client.post(f"/api/projects/{project['id']}/export?format=wav")
        self.assertEqual(exported.status_code,200,exported.text)
        audio,rate=sf.read(io.BytesIO(exported.content));self.assertEqual(rate,24000);self.assertTrue(len(audio)>0)
        ffmpeg=os.environ.get('VOZ_LOCAL_FFMPEG') or __import__('shutil').which('ffmpeg')
        if ffmpeg:
            exported=self.client.post(f"/api/projects/{project['id']}/export?format=mp3")
            self.assertEqual(exported.status_code,200,exported.text)
        self.assertTrue(self.client.get(f"/api/projects/{project['id']}").is_success)

    def test_fragment_order_and_independent_regeneration(self):
        import numpy as np
        import soundfile as sf
        identifier='d'*32
        voice=self.root/'voices'/f'{identifier}.wav'
        sf.write(voice,np.zeros(24000,dtype=np.float32),24000)
        with self.storage.connection() as db:
            db.execute('INSERT OR IGNORE INTO voices(id,name,transcript,sample_path,duration) VALUES (?,?,?,?,?)',(identifier,'Order test','Hello','voices/'+voice.name,1.0))
        script=('First part with several spoken words. '*12)+('Second part with different spoken words. '*12)
        response=self.client.post('/api/projects',json={'title':'Ordered parts','voice_id':identifier,'script':script,'mode':'fragments'})
        self.assertEqual(response.status_code,200,response.text)
        project=response.json();chunks=project['chunks'];self.assertGreater(len(chunks),1)
        values=[]
        for index,chunk in enumerate(chunks):
            value=(index+1)/100
            values.append(value)
            with patch.object(self.main.engine,'generate',return_value=(np.full(2400,value,dtype=np.float32),24000,'0.6B')):
                generated=self.client.post(f"/api/projects/{project['id']}/chunks/{chunk['id']}/generate")
                self.assertEqual(generated.status_code,200,generated.text)
        preserved=self.client.get(f"/api/projects/{project['id']}").json()['chunks'][0]['audio_url']
        first=self.client.get(preserved).content
        with patch.object(self.main.engine,'generate',return_value=(np.full(2400,.25,dtype=np.float32),24000,'0.6B')):
            self.assertEqual(self.client.post(f"/api/projects/{project['id']}/chunks/{chunks[1]['id']}/generate").status_code,200)
        self.assertEqual(self.client.get(preserved).content,first)
        values[1]=.25
        result=self.client.post(f"/api/projects/{project['id']}/export?format=wav")
        self.assertEqual(result.status_code,200,result.text)
        audio,rate=sf.read(io.BytesIO(result.content))
        self.assertEqual(len(audio),len(chunks)*2400)
        for index,value in enumerate(values):self.assertAlmostEqual(float(np.mean(audio[index*2400:(index+1)*2400])),value,places=3)

if __name__=='__main__':unittest.main()
