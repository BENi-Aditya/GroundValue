"""Start the local app independently of a temporary command session."""
from pathlib import Path
import fcntl
import json
import subprocess
import time
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parent
DATA = ROOT / 'data'
URL = 'http://127.0.0.1:8501'

def healthy():
    try:
        with urlopen(URL + '/_stcore/health', timeout=2) as response:
            return response.status == 200 and response.read() == b'ok'
    except OSError:
        return False

def main():
    DATA.mkdir(exist_ok=True)
    with (DATA / 'server.lock').open('w') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        if healthy():
            print('Streamlit is already responding at ' + URL)
            return
        python = ROOT / '.venv/bin/python'
        if not python.exists():
            raise SystemExit('Create .venv and install requirements.txt first.')
        with (DATA / 'server.log').open('ab') as log:
            process = subprocess.Popen(
                [str(python), '-m', 'streamlit', 'run', 'app.py',
                 '--server.address', '127.0.0.1', '--server.port', '8501',
                 '--browser.gatherUsageStats', 'false'], cwd=ROOT,
                stdin=subprocess.DEVNULL, stdout=log, stderr=log,
                start_new_session=True, close_fds=True)
        (DATA / 'server.json').write_text(json.dumps({'pid': process.pid, 'url': URL}))
        for _ in range(40):
            if process.poll() is not None:
                raise SystemExit('Server exited. See groundvalue/data/server.log.')
            if healthy():
                print(f'GroundValue is running at {URL} (PID {process.pid}).')
                return
            time.sleep(.25)
        raise SystemExit('Startup is taking longer than expected. See groundvalue/data/server.log.')

if __name__ == '__main__':
    main()
