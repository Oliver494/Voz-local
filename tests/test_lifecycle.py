import os
from pathlib import Path
import subprocess
import sys
import unittest

@unittest.skipUnless(sys.platform=='linux','Linux process-group crash cleanup')
class ParentDeathTests(unittest.TestCase):
    def test_parent_crash_stops_own_worker_group(self):
        parent=subprocess.Popen([sys.executable,'-c','import time; time.sleep(60)'],start_new_session=True)
        worker=None
        try:
            helper=Path(__file__).resolve().parents[1]/'scripts/desktop/lifecycle.py'
            code=f"import runpy,time; runpy.run_path({str(helper)!r}); print('ready',flush=True); time.sleep(60)"
            worker=subprocess.Popen([sys.executable,'-c',code],env=dict(os.environ,VOZ_LOCAL_PARENT_PID=str(parent.pid)),start_new_session=True,stdout=subprocess.PIPE,text=True)
            self.assertEqual(worker.stdout.readline().strip(),'ready')
            parent.terminate();parent.wait(timeout=5)
            self.assertEqual(worker.wait(timeout=5),-9)
        finally:
            if worker is not None:
                if worker.poll() is None:worker.kill();worker.wait()
                worker.stdout.close()
            if parent.poll() is None:parent.kill();parent.wait()
