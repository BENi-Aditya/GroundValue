"""Visual workspace shell; research controls and calculation remain in app.py."""
import html
import streamlit as st

def render_shell():
    if 'day_mode' not in st.session_state:
        st.session_state.day_mode = st.query_params.get('theme') == 'light'
    with st.sidebar:
        st.markdown('## ⌂ GroundValue')
        st.caption('YOUR PROPERTY WORKSPACE')
        day = st.toggle('Day mode ☀', key='day_mode')
        st.markdown('[Explore GroundValue ↗](http://localhost:8080/)')
        st.divider()
    st.query_params['theme'] = 'light' if day else 'dark'
    bg, surface, ink, muted, shadow, highlight = ('#edf0e9','#edf0e9','#173d32','#607467','#c7d1c1','#ffffff') if day else ('#14231e','#1b2d25','#dfecdd','#adc1b0','#091610','#2c4434')
    st.markdown(f'''<style>
    :root{{--gv-bg:{bg};--gv-surface:{surface};--gv-ink:{ink};--gv-muted:{muted}}}
    .stApp,[data-testid="stHeader"]{{background:{bg};color:{ink}}}
    [data-testid="stSidebar"]{{background:{surface};border-right:1px solid {highlight}55}}
    .stApp h1,.stApp h2,.stApp h3,.stApp p,.stApp label,.stApp summary{{color:{ink}}}
    .stApp [data-testid="stCaptionContainer"] p{{color:{muted}}}
    .block-container{{max-width:1280px;padding:2.2rem 3rem}}
    [data-testid="stForm"],[data-testid="stMetric"],[data-testid="stExpander"],.gv-card{{background:{surface};border:1px solid {highlight}55!important;border-radius:22px;padding:24px;box-shadow:8px 8px 20px {shadow},-6px -6px 18px {highlight}}}
    .stApp input,.stApp [data-baseweb="select"]>div{{background:{bg}!important;color:{ink}!important;border-color:{highlight}!important;border-radius:12px!important}}
    .stApp button{{border-radius:12px!important}}
    .stApp button[kind="primary"]{{background:#b5cfae;color:#14271e;border:0;box-shadow:4px 4px 12px {shadow}}}
    .gv-hero{{position:relative;overflow:hidden;border-radius:26px;padding:32px;margin:8px 0 28px;background:linear-gradient(120deg,{surface}, {highlight});box-shadow:8px 8px 22px {shadow},-5px -5px 18px {highlight};animation:gv-day .85s ease both}}
    .gv-hero h2{{font-size:32px;margin:8px 0 12px}}.gv-hero p{{max-width:620px;color:{muted}}}
    .gv-kicker{{font:11px monospace;letter-spacing:2px;color:{muted}}}.gv-flow{{display:flex;gap:12px;flex-wrap:wrap;margin:24px 0 0}}.gv-flow span{{padding:10px 15px;border-radius:12px;background:{bg};color:{ink};font-size:12px;box-shadow:inset 3px 3px 7px {shadow},inset -3px -3px 7px {highlight}}}
    .gv-sky{{position:absolute;right:28px;top:24px;font-size:44px;color:#e9c87d;filter:drop-shadow(0 0 18px #e9c87d55)}}
    @keyframes gv-day{{from{{opacity:.3;transform:translateY(8px);filter:blur(4px)}}to{{opacity:1;transform:none;filter:none}}}}
    @media(max-width:700px){{.block-container{{padding:1.5rem 1rem}}.gv-hero{{padding:24px}}.gv-hero h2{{font-size:27px}}.gv-sky{{display:none}}}}
    @media(prefers-reduced-motion:reduce){{.gv-hero{{animation:none}}}}
    </style>''', unsafe_allow_html=True)
    st.markdown(f'''<div class="gv-hero"><div class="gv-sky">{'☀' if day else '☾'}</div><div class="gv-kicker">GROUNDVALUE / YOUR RESEARCH DESK</div><h2>Your property research</h2><p>Research an apartment, follow the agent’s progress, and review the evidence behind its asking-price estimate.</p><div class="gv-flow"><span>01 · Property details</span><span>02 · Source research</span><span>03 · Evidence & report</span></div></div>''',unsafe_allow_html=True)
