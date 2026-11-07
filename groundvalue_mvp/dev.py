"""Compatibility launcher for the session-independent GroundValue web app."""
import runpy
if __name__ == '__main__':
    runpy.run_module('web',run_name='__main__')
