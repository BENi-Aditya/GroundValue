"""Render provider activity without inventing progress percentages or browser actions."""
from html import escape
import time
from urllib.parse import urlsplit
import streamlit as st

def preview_url(value):
    if not isinstance(value,str): return None
    try:
        parsed=urlsplit(value);host=(parsed.hostname or '').lower()
        trusted=(host.endswith('.unikraft.app') and host.startswith('tf-')) or host=='agent.tinyfish.ai' or host.endswith('.tinyfish.ai') or host.endswith('.tinyfish.io')
        if parsed.scheme=='https' and trusted and not parsed.username and not parsed.password and parsed.port in (None,443):
            return value
    except ValueError:pass
    return None

def render_activity(job):
    active=job['state']=='running'
    elapsed=max(0,int(time.time()-job['started'])) if active else job.get('elapsed_seconds',0)
    actions=[e for e in job['events'] if e['kind']=='action']
    sources=job['sources']
    st.subheader('Live research studio' if active else 'Research activity')
    a,b,c=st.columns(3)
    a.metric('Elapsed',f'{elapsed//60:02d}:{elapsed%60:02d}')
    b.metric('Browser actions',len(actions))
    c.metric('Status','Stopping…' if job.get('stop_requested') and active else job['state'].capitalize())
    current=job['events'][-1]['message'] if job['events'] else 'Starting TinyFish research…'
    st.info(current)
    left,right=st.columns([1.65,1])
    with left:
        st.caption('TINYFISH BROWSER · READ-ONLY LIVE VIEW')
        viewers=[(name,preview_url(v.get('streaming_url'))) for name,v in sources.items()
                 if v.get('status') in ('running','pending','queued')]
        viewers=[(name,url) for name,url in viewers if url]
        if active and viewers:
            name,url=viewers[-1]
            st.iframe(url,height=460)
            st.link_button('Open live browser in a new tab',url)
            st.caption('The view may expire after the run. If embedding is blocked, use the link above.')
        else:
            label='Waiting for TinyFish to open its browser' if active else ('Browser session ended' if any(v.get('run_id') for v in sources.values()) else 'No browser session was started')
            detail='Real actions will appear on the right as the agent works.' if active else 'The activity trail remains available below.'
            st.markdown(f'<div class="browser-placeholder"><div class="browser-icon">⌕</div><h3>{label}</h3><p>{detail}</p></div>',unsafe_allow_html=True)
    with right:
        st.caption('ACTIVITY TRAIL · REAL PROVIDER EVENTS')
        with st.container(height=490):
            for event in reversed(job['events'][-60:]):
                source=escape(event['source']);message=escape(event['message'])
                stamp=escape(event['at'][11:19])
                st.markdown(f'<div class="activity-event"><span>{source} · {stamp} UTC</span><p>{message}</p></div>',unsafe_allow_html=True)
            if not job['events']:st.caption('Waiting for the first update.')
    with st.expander('Run identifiers and source pages'):
        for name,source in sources.items():
            st.write(name)
            if source.get('run_id'):st.code(source['run_id'])
            if source.get('page_url'):st.write(source['page_url'])
