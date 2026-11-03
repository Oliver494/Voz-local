"""Linux crash cleanup: a dead desktop parent must not leave a GPU worker behind."""
import os
import signal
import sys
import threading
import time

def watch_parent():
    if sys.platform!='linux' or not os.environ.get('VOZ_LOCAL_PARENT_PID'):return
    parent=int(os.environ['VOZ_LOCAL_PARENT_PID'])
    group=os.getpgrp()
    if group != os.getpid() and not (group == os.getppid() and group != parent):return
    def start_marker():
        try:return open(f'/proc/{parent}/stat').read().split(') ',1)[1].split()[19]
        except OSError:return None
    marker=start_marker()
    def monitor():
        while True:
            if marker is None or start_marker()!=marker:
                # All desktop workers start in their own process group; never kill the host shell.
                os.killpg(group,signal.SIGKILL)
                return
            time.sleep(.5)
    threading.Thread(target=monitor,daemon=True).start()

watch_parent()
