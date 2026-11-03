"""Explicitly create an empty, synthetic library for native CI media verification."""
import argparse
import json
import math
import os
from pathlib import Path
import sqlite3
import struct
import sys
import wave

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--data',required=True)
    args=parser.parse_args()
    root=Path(args.data).resolve()
    if (root/'voz_local.sqlite3').exists():raise SystemExit('Refusing to overwrite an existing library')
    root.mkdir(parents=True,exist_ok=True)
    os.environ['VOZ_LOCAL_DATA_DIR']=str(root)
    sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
    from app import storage
    storage.initialize()
    voice,project,chunk='a'*32,'b'*32,'c'*32
    folder=root/'projects'/project;folder.mkdir(exist_ok=True)
    for path in (root/'voices'/f'{voice}.wav',folder/f'{chunk}.wav',folder/f'{chunk}.raw.wav'):
        with wave.open(str(path),'wb') as out:
            out.setnchannels(1);out.setsampwidth(2);out.setframerate(24000)
            out.writeframes(b''.join(struct.pack('<h',int(1000*math.sin(i*2*math.pi*440/24000))) for i in range(24000)))
    with storage.connection() as db:
        db.execute('INSERT INTO voices(id,name,transcript,sample_path,duration) VALUES (?,?,?,?,?)',(voice,'Synthetic native test','Hello',f'voices/{voice}.wav',1.))
        db.execute('INSERT INTO projects(id,title,voice_id,script,mode,settings) VALUES (?,?,?,?,?,?)',(project,'Native media test',voice,'Hello','continuous','{}'))
        db.execute('INSERT INTO chunks(id,project_id,position,text,audio_path,model_size) VALUES (?,?,?,?,?,?)',(chunk,project,0,'Hello',f'projects/{project}/{chunk}.wav','synthetic'))
    (root/'desktop-settings.json').write_text(json.dumps({'profile':'cpu','model':'0.6B'}))
    (root/'desktop-ready.json').write_text('synthetic CI fixture; no TTS installation validation')
    (root/'environment-ready.json').write_text('{}')
