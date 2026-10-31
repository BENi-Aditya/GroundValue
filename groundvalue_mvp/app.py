from pathlib import Path
import streamlit as st
from core import Property,BASES,analyse
from sample import observations
from research import SOURCES
from tinyfish_client import load_key
from report import rupees,csv_report,html_report
from storage import save,latest_live
from jobs import get_manager
from progress_ui import render_activity

st.set_page_config(page_title='GroundValue',page_icon='⌂',layout='wide',initial_sidebar_state='collapsed')
if st.query_params.get('view') != 'app':
    import streamlit.components.v1 as components
    st.markdown("""<style>
        .block-container{padding:0!important;max-width:none!important;margin:0!important}
        header[data-testid='stHeader']{display:none!important}
        iframe{border:0!important;margin:0!important;padding:0!important;width:100vw!important;height:100vh!important;position:fixed!important;top:0!important;left:0!important}
        footer{display:none!important}
        .main{padding:0!important;margin:0!important}
        section[data-testid='stMain']{padding:0!important;margin:0!important}
        div[data-testid='stAppViewContainer']{padding:0!important;margin:0!important}
        html,body{margin:0!important;padding:0!important;overflow:hidden!important;width:100vw!important;height:100vh!important}
        section.main{overflow:hidden!important}
    </style>""", unsafe_allow_html=True)
    landing = Path(__file__).parent / 'landing'
    page = (landing / 'index.html').read_text()
    module = (landing / 'scene.js').read_text().replace("import * as THREE from './three.module.js';", '')
    library = (landing / 'three.module.js').read_text()
    import base64
    library_url = 'data:text/javascript;base64,' + base64.b64encode(library.encode()).decode()
    page = page.replace('<script type="module" src="scene.js"></script>', '<script type="module">import * as THREE from "' + library_url + '";\n' + module + '</script>')
    page = page.replace('http://127.0.0.1:8501/?view=app', '?view=app')
    # Add script to make iframe responsive
    page = page.replace('</body>', """<script>
if(window.parent!==window){
  function updateHeight(){window.parent.postMessage({type:'streamlit:setComponentValue',height:document.documentElement.scrollHeight},'*')}
  window.addEventListener('load',updateHeight);
  window.addEventListener('resize',updateHeight);
  new ResizeObserver(updateHeight).observe(document.body);
}
</script></body>""")
    components.html(page, height=3000, scrolling=True)
    st.stop()
from application import render
render()
