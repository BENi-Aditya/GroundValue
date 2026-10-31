"""Shared architectural illustrations and the application design system."""
import streamlit as st

def building_cover():
    windows=''.join(f'<rect x="{x}" y="{y}" width="17" height="25" fill="#667d79"/><path d="M{x+8} {y}v25" stroke="#c9d0c0"/>' for x in (132,160,188,216) for y in (62,98,134,170))
    rails=''.join(f'<path d="M116 {y}h126v9H116z" fill="#e5e5d6"/><path d="M119 {y-10}h120M122 {y-10}v10m15-10v10m15-10v10m15-10v10m15-10v10m15-10v10m15-10v10m15-10v10" stroke="#8d9d8d" fill="none"/>' for y in (90,126,162,198))
    return '<div class="property-cover"><svg viewBox="0 0 380 240" xmlns="http://www.w3.org/2000/svg"><defs><linearGradient id="sky" x2="0" y2="1"><stop stop-color="#c0d4d9"/><stop offset="1" stop-color="#e8e9de"/></linearGradient></defs><rect width="380" height="240" fill="url(#sky)"/><path d="M0 195L380 182v58H0" fill="#b8c3a9"/><path d="M75 232l174-15 100 23" fill="#e9e7da"/><path d="M105 50l32-20 116 10-15 16z" fill="#ececdf"/><path d="M105 50v152l31 17V42z" fill="#a9b4a4"/><path d="M128 44h119v174H128z" fill="#d8d8c4"/>'+windows+rails+'<path d="M124 43h128v10H124z" fill="#f1f0e5"/><path d="M170 32h44v12h-44z" fill="#b9c2b2"/><rect x="170" y="201" width="27" height="18" fill="#6a7a6c"/><g fill="#7b936c"><circle cx="73" cy="153" r="26"/><circle cx="56" cy="167" r="19"/><circle cx="299" cy="155" r="29"/><circle cx="320" cy="174" r="21"/></g><g fill="#9eaf88"><circle cx="65" cy="145" r="16"/><circle cx="289" cy="145" r="19"/></g><path d="M72 164v60m230-60v59" stroke="#7a8067" stroke-width="5"/><path d="M0 230h380" stroke="#a5b19c"/></svg><span>Architectural illustration</span></div>'

def location_card():
    roads=''.join(f'<path d="M{x} 0l-80 350"/>' for x in range(0,600,65))+''.join(f'<path d="M0 {y}l500 40"/>' for y in range(20,350,55))
    return '<div class="location-card"><svg viewBox="0 0 500 350"><rect width="500" height="350" fill="#e0e5d9"/><g stroke="#f8f8f1" stroke-width="9">'+roads+'</g><g stroke="#bac8af" stroke-width="1" fill="none">'+roads+'</g><path d="M192 132l73 7-12 74-80-9z" fill="#96ae8f" stroke="#477457" stroke-width="2"/><circle cx="222" cy="157" r="15" fill="#234c3a"/><circle cx="222" cy="157" r="5" fill="white"/></svg><div class="location-label"><b>Electronic City</b><br>Bengaluru, Karnataka</div><small>Location illustration · not a geographic map</small></div>'

def style(dark,page):
    paper,surface,ink,muted,edge,shadow,light=('#191c20','#23272c','#e7e9e8','#adb6b7','#353c41','#111417','#30373c') if dark else ('#f5f5ef','#f5f6f0','#172c23','#708077','#e1e5dc','#d9ded2','#ffffff')
    st.markdown(f'''<style>
    [data-testid="stSidebar"]{{min-width:216px!important;max-width:216px!important;background:{paper}!important;border:0!important}}
    [data-testid="stSidebarUserContent"]{{padding:30px 16px!important}}
    [data-testid="stSidebar"] h2{{font-size:21px!important;letter-spacing:-.8px;margin-bottom:25px}}
    [data-testid="stSidebar"] button{{width:100%;border:0!important;background:transparent!important;box-shadow:none!important;text-align:left;justify-content:flex-start;padding:12px 14px!important}}
    [data-testid="stSidebar"] button p{{font-size:13px!important}}
    [data-testid="stSidebar"] button:hover{{background:{edge}!important}}
    .st-key-nav_{'New_Research' if page=='new' else 'Home'} button{{background:{edge}!important;box-shadow:inset 2px 2px 5px {shadow},inset -2px -2px 5px {light}!important}}
    .block-container{{max-width:1450px;padding:44px 38px 80px!important}}
    [data-testid="stHeader"]{{height:0;background:transparent!important}}[data-testid="stToolbar"]{{display:none}}
    h1{{font-size:28px!important;font-weight:650!important;letter-spacing:-.8px!important;padding-top:0!important}}h3{{font-size:17px!important;line-height:1.35!important}}
    .stApp{{background:{paper}!important}}.stApp p{{font-size:14px}}[data-testid="stCaptionContainer"] p{{font-size:12px!important}}
    [data-testid="stVerticalBlockBorderWrapper"]>div,[data-testid="stForm"], [data-testid="stMetric"]{{background:{surface}!important;border:1px solid {light}66!important;box-shadow:6px 6px 17px {shadow},-6px -6px 17px {light};border-radius:14px!important}}
    [data-testid="stForm"]{{padding:24px!important}}
    [data-testid="stTextInput"]>div,[data-testid="stNumberInput"]>div,[data-testid="stTextArea"]>div,[data-baseweb="select"]>div{{border:1px solid {edge}!important;border-radius:9px!important;box-shadow:inset 2px 2px 5px {shadow},inset -2px -2px 5px {light}!important;background:{surface}!important}}
    .stApp button{{border-radius:9px!important;box-shadow:3px 3px 8px {shadow},-3px -3px 8px {light};border:1px solid {edge}!important}}
    .stApp button[kind="primary"],.stApp button[data-testid="stBaseButton-primaryFormSubmit"]{{background:#234e3a!important;color:white!important;border:0!important}}
    .stApp button[kind="primary"] p,.stApp button[data-testid="stBaseButton-primaryFormSubmit"] p{{color:white!important}}
    .property-cover{{position:relative;height:190px;overflow:hidden;border-radius:9px;margin-bottom:3px;background:#dce3d5}}
    .property-cover svg{{height:100%;width:100%;object-fit:cover}}.property-cover span{{position:absolute;right:8px;bottom:7px;font-size:8px;letter-spacing:.6px;text-transform:uppercase;background:#f7f7efcf;color:#4b6252;padding:3px 6px;border-radius:3px}}
    .location-card{{height:350px;position:relative;border-radius:14px;overflow:hidden;box-shadow:inset 3px 3px 10px {shadow},5px 5px 15px {shadow}}}.location-card svg{{height:100%;width:100%;object-fit:cover}}.location-label{{position:absolute;top:32px;right:25px;background:{surface};color:{ink};padding:16px 22px;border-radius:12px;box-shadow:3px 3px 12px #0001;font-size:13px}}.location-card small{{position:absolute;bottom:12px;left:12px;font-size:10px;background:{surface};color:{muted};padding:6px 10px;border-radius:6px}}
    .steps-bar{{display:flex;gap:22px;font-size:12px;color:{muted};margin:8px 0 28px}}.steps-bar span{{display:flex;gap:8px;align-items:center}}.steps-bar b{{border-radius:50%;background:{edge};padding:5px 10px;font-size:11px}}.steps-bar span:first-child{{color:{ink}}}.steps-bar span:first-child b{{background:#234e3a;color:white}}
    .type-chip{{display:inline-block;border:1px solid {edge};border-radius:8px;padding:8px 12px;margin:0 6px 12px 0;background:{surface};font-size:12px;color:{ink}}}
    .library-value{{font-size:20px;font-weight:650;color:{ink};margin:12px 0 4px}}.sidebar-footer{{margin-top:80px;border-top:1px solid {edge};padding:20px 10px;font-size:12px;color:{muted}}}
    [data-testid="stTabs"] button{{box-shadow:none;border-radius:0!important}}[data-testid="stMetric"]{{padding:20px}}[data-testid="stMetricValue"]{{font-size:27px!important}}
    @media(max-width:900px){{.block-container{{padding:30px 20px!important}}.property-cover{{height:150px}}}}
    @media(max-width:640px){{.block-container{{padding:24px 16px!important}}.steps-bar{{gap:10px;flex-wrap:wrap}}.location-card{{height:260px}}}}
    </style>''',unsafe_allow_html=True)
