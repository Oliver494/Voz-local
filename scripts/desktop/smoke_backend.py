"""Opt-in real-model desktop protocol smoke test. Never modifies the source library."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import sqlite3
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
import uuid
import wave


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--legacy-data',required=True)
    parser.add_argument('--voice-name',required=True)
    parser.add_argument('--output',required=True)
    parser.add_argument('--model',choices=['1.7B','0.6B'],default='1.7B')
    args=parser.parse_args()
    source=Path(args.legacy_data).resolve();output=Path(args.output).resolve();output.mkdir(parents=True,exist_ok=True)
    with sqlite3.connect((source/'voz_local.sqlite3').as_uri()+'?mode=ro',uri=True) as db:
        db.row_factory=sqlite3.Row
        voice=db.execute('SELECT * FROM voices WHERE name=?',(args.voice_name,)).fetchone()
        if voice is None:raise ValueError('Requested voice profile does not exist')
        voice=dict(voice)
    original=(source/voice['sample_path']).resolve()
    if source not in original.parents:raise ValueError('Invalid sample path')
    original_hash=hashlib.sha256(original.read_bytes()).hexdigest()
    with tempfile.TemporaryDirectory(prefix='voz-desktop-smoke-') as temp:
        data=Path(temp);token=uuid.uuid4().hex+uuid.uuid4().hex
        env=dict(os.environ,VOZ_LOCAL_DATA_DIR=str(data),VOZ_LOCAL_MODELS_DIR=str(source/'models'),VOZ_LOCAL_DEFAULT_MODEL=args.model,TORCH_ROCM_AOTRITON_ENABLE_EXPERIMENTAL='1')
        root=Path(__file__).resolve().parents[2]
        # Initialize only the isolated test DB, not the source library.
        subprocess.run([sys.executable,'-c','from app.storage import initialize; initialize()'],cwd=root,env=env,check=True)
        sample=data/'voices'/f"{voice['id']}.wav";shutil.copy2(original,sample)
        with sqlite3.connect(data/'voz_local.sqlite3') as db:
            db.execute('INSERT INTO voices(id,name,transcript,sample_path,duration) VALUES (?,?,?,?,?)',(voice['id'],'Private smoke sample',voice['transcript'],str(sample.relative_to(data)),voice['duration']))
        logs=open(output/'engine.log','w')
        kwargs={'start_new_session':True} if os.name!='nt' else {'creationflags':subprocess.CREATE_NEW_PROCESS_GROUP}
        process=subprocess.Popen([sys.executable,str(root/'scripts/desktop/server.py')],cwd=root,env=env,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=logs,text=True,**kwargs)
        try:
            process.stdin.write(json.dumps({'token':token})+'\n');process.stdin.close()
            ready=json.loads(process.stdout.readline());base='http://127.0.0.1:'+str(ready['port'])
            def request(path,method='GET',body=None,auth=True,headers=None):
                data=json.dumps(body).encode() if body is not None else None
                fields={'Content-Type':'application/json',**(headers or {})}
                if auth:fields['Authorization']='Bearer '+token
                req=urllib.request.Request(base+path,data=data,method=method,headers=fields)
                with urllib.request.urlopen(req,timeout=600) as response:return response.status,response.read()
            for _ in range(60):
                try:status=json.loads(request('/api/status')[1]);break
                except (OSError,urllib.error.URLError):time.sleep(1)
            else:raise RuntimeError('Sidecar did not become ready')
            try:request('/api/voices',auth=False);raise AssertionError('Missing token was accepted')
            except urllib.error.HTTPError as error:assert error.code==401
            project=json.loads(request('/api/projects','POST',{'title':'Desktop smoke','voice_id':voice['id'],'script':'Hola, esta es una prueba breve de Voz Local.','mode':'continuous','voice_model':'qwen-'+args.model.lower()})[1])
            # Model IDs use lower-case b in settings.
            chunk=project['chunks'][0]
            started=time.monotonic()
            generated=json.loads(request(f"/api/projects/{project['id']}/chunks/{chunk['id']}/generate",'POST')[1])
            elapsed=time.monotonic()-started
            wav=request(generated['audio_url'])[1];(output/'desktop-original.wav').write_bytes(wav)
            code,partial=request(generated['audio_url'],headers={'Range':'bytes=0-43'});assert code==206 and len(partial)==44
            for format in ('wav','mp3'):
                content=request(f"/api/projects/{project['id']}/export?format={format}",'POST')[1]
                assert len(content)>100
                (output/f'desktop-export.{format}').write_bytes(content)
            with wave.open(str(output/'desktop-original.wav')) as audio:
                duration=audio.getnframes()/audio.getframerate();rate=audio.getframerate();assert duration>0.2
            assert hashlib.sha256(original.read_bytes()).hexdigest()==original_hash
            report={'backend':status['runtime'],'model':args.model,'seconds':round(elapsed,2),'audio_duration':duration,'sample_rate':rate,'authorization':'401 without token','range':'206','exports':['wav','mp3'],'source_sample_unchanged':True,'perceived_voice_quality':'requires listening'}
            (output/'result.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
        finally:
            if os.name!='nt':os.killpg(process.pid,signal.SIGTERM)
            else:process.terminate()
            try:process.wait(timeout=15)
            except subprocess.TimeoutExpired:process.kill();process.wait()
            logs.close()
            assert process.poll() is not None

if __name__=='__main__':main()
