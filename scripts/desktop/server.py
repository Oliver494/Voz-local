"""Private desktop server. Token arrives through stdin, never the command line."""
import json
if __name__ == "__main__":
    import lifecycle
import os
from pathlib import Path
import socket
import sys

root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(root))
credentials = json.loads(sys.stdin.readline())
if len(credentials.get('token', '')) < 32:
    raise SystemExit('Missing session credentials')
os.environ['VOZ_LOCAL_SESSION_TOKEN'] = credentials['token']
from import_data import recover_import
recover_import(Path(os.environ["VOZ_LOCAL_DATA_DIR"]))
import uvicorn
from app.main import app

listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
listener.bind(('127.0.0.1', 0))
listener.listen(128)
print(json.dumps({'event': 'ready', 'port': listener.getsockname()[1]}), flush=True)
uvicorn.Server(uvicorn.Config(app, log_level='info', access_log=False)).run(sockets=[listener])
