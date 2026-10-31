"""Serve the landing page and existing research app with one command."""
from pathlib import Path
import subprocess
import sys
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from functools import partial
ROOT = Path(__file__).resolve().parent
if __name__ == '__main__':
    app = subprocess.Popen([sys.executable, '-m', 'streamlit', 'run', str(ROOT / 'app.py'), '--server.address', '127.0.0.1', '--server.port', '8501', '--server.headless', 'true', '--browser.gatherUsageStats', 'false'], cwd=ROOT)
    try:
        print('GroundValue landing page: http://localhost:8080/', flush=True)
        ThreadingHTTPServer(('127.0.0.1', 8080), partial(SimpleHTTPRequestHandler, directory=str(ROOT / 'landing'))).serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        app.terminate()
        app.wait()
