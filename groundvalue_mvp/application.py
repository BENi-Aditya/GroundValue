"""Property library and real research workspace."""
import json,html
import streamlit as st
import projects
from design import style,building_cover,location_card
from core import Property,BASES
from jobs import get_manager
from tinyfish_client import load_key
from research import SOURCES
from progress_ui import render_activity
from report import rupees,csv_report,html_report
from excel_export import workbook

def navigate(page,pid=None):
    st.query_params['page']=page
    if pid:st.query_params['property']=pid
    elif 'property' in st.query_params:del st.query_params['property']
    st.rerun()

def render():
    projects.import_legacy()
    if 'app_dark' not in st.session_state:st.session_state.app_dark=False
    with st.sidebar:
        st.markdown('## ⬡ GroundValue')
        for name,page in [('Home','home'),('New Research','new'),('Saved Properties','home')]:
            if st.button(name,use_container_width=True,key='nav_'+name):navigate(page)
        st.divider()
        if st.button('◐',help='Switch appearance',key='appearance'):st.session_state.app_dark=not st.session_state.app_dark;st.rerun()
        st.markdown('<div class="sidebar-footer"><b>Local workspace</b><br>Saved on this computer</div>',unsafe_allow_html=True)
        st.markdown('[About GroundValue ↗](http://localhost:8080/)')
    dark=st.session_state.app_dark
    bg,card,text,muted,border=('#17191c','#22252a','#e7e8e9','#aeb4ba','#363b42') if dark else ('#F7F7F2','#ffffff','#172720','#65756B','#DFE5DD')
    st.markdown(f'''<style>
    .stApp,[data-testid="stHeader"]{{background:{bg};color:{text}}}
    [data-testid="stSidebar"]{{background:{'#1d2024' if dark else '#F0F3ED'};border-right:1px solid {border}}}
    .block-container{{max-width:1350px;padding:2.5rem 3rem}}h1{{font-size:32px!important}}h2{{font-size:24px!important}}
    .stApp p,.stApp label,.stApp h1,.stApp h2,.stApp h3,.stApp summary{{color:{text}}}
    [data-testid="stCaptionContainer"] p{{color:{muted}!important}}
    [data-testid="stVerticalBlockBorderWrapper"]>div,[data-testid="stForm"],[data-testid="stMetric"]{{border-radius:12px!important;border-color:{border}!important;background:{card}}}
    .stApp input,.stApp textarea,.stApp [data-baseweb="select"]>div,.stApp [data-baseweb="input"],.stApp [data-baseweb="base-input"]{{background:{card}!important;color:{text}!important;border-color:{border}!important}}
    .stApp [data-baseweb="select"],.stApp [data-baseweb="select"]>div{{background:{card}!important;border:1px solid {border}!important}}
    .stApp input:disabled{{-webkit-text-fill-color:{muted}!important}}[data-baseweb="popover"],[role="listbox"]{{background:{card}!important;color:{text}!important}}
    .browser-placeholder{{padding:40px;border:1px solid {border};border-radius:12px;min-height:340px;display:grid;place-content:center;text-align:center;background:{card}}}.activity-event{{border-left:2px solid #8FA99A;padding:6px 14px;margin:12px 0}}.activity-event span{{font-size:11px;color:{muted}}}
    .stApp button{{border-radius:8px!important;background:{card};color:{text};border-color:{border}}}
    .stApp button[kind="primary"] p{{color:#fff!important}}
    .stApp button[kind="primary"]{{background:#173D32;color:#fff;border-color:#173D32}}
    .cover{{height:130px;border-radius:9px;background:linear-gradient(135deg,{'#30383f,#22272d' if dark else '#eef1e9,#dce4d9'});display:flex;align-items:center;justify-content:center;margin-bottom:16px;position:relative;overflow:hidden}}
    .cover svg{{width:150px;height:115px;stroke:{'#a5b4be' if dark else '#7e9587'};fill:none;stroke-width:1.2}}.cover small{{position:absolute;bottom:6px;right:10px;font-size:9px;color:{muted}}}
    @media(max-width:700px){{.block-container{{padding:1.5rem 1rem}}}}
    </style>''',unsafe_allow_html=True)
    manager=get_manager();job=manager.snapshot();busy=bool(job and job['state']=='running')
    page=st.query_params.get('page','home');style(dark,page);pid=st.query_params.get('property');project=projects.get(pid) if pid else None
    if busy:
        st.info('Research is running. You can return to its workspace without starting another session.')
        if st.button('View active research'):navigate('property',job.get('project_id'))
    cover=building_cover()
    if page=='home':
        a,b=st.columns([4,1]);a.title('Your Property Research');a.caption('View and manage your saved property research.')
        if b.button('+ New Property',type='primary'):navigate('new')
        a,b,c=st.columns([3,1.5,1.5]);search=a.text_input('Search properties',placeholder='Search properties, locations…',label_visibility='collapsed');status=b.selectbox('Status',['All','Not researched','running','completed','failed','stopped'],label_visibility='collapsed');order=c.selectbox('Sort by',['Last updated','Name'],label_visibility='collapsed')
        items=projects.listing()
        if order=='Name':items.sort(key=lambda p:p['name'].lower())
        items=[p for p in items if search.lower() in (p['name']+p['details']).lower()]
        visible=[]
        for p in items:
            history=projects.runs(p['id']);state=history[0]['status'] if history else 'Not researched'
            if status=='All' or status==state:visible.append((p,history,state))
        if not visible:
            st.info('No saved properties' if not items else 'No properties match these filters.')
            st.write('Create a property to start a research session.')
        for start in range(0,len(visible),3):
            for col,(p,history,state) in zip(st.columns(3),visible[start:start+3]):
                with col,st.container(border=True):
                    st.markdown(cover,unsafe_allow_html=True);st.subheader(p['name']);d=json.loads(p['details']);st.caption('Electronic City, Bengaluru · Apartment')
                    result=(history[0]['snapshot'].get('report') or {}) if history else {};estimate=result.get('estimate')
                    st.markdown('<div class="library-value">'+(rupees(estimate['value']) if estimate else 'Not estimated')+'</div>',unsafe_allow_html=True)
                    st.caption(f"{state} · {len(history)} saved runs · {p['updated'][:10]}")
                    if st.button('Open property →',key=p['id'],use_container_width=True):navigate('property',p['id'])
        return
    if page=='new':
        st.caption('HOME / PROPERTY DETAILS');st.title('Add Property Details');st.markdown('<div class="steps-bar"><span><b>1</b> Property details</span><span><b>2</b> Live research</span><span><b>3</b> Results</span></div>',unsafe_allow_html=True)
        defaults=project['details'] if project else {};a,b=st.columns([1.35,1])
        with b:
            st.markdown(location_card(),unsafe_allow_html=True);st.caption('Research coverage: Electronic City, Bengaluru. Address and notes are saved with this property; location search is not yet available.')
        with a,st.form('new_property'):
            st.markdown('<span class="type-chip">⌂ Residential</span><span class="type-chip">Apartment</span>',unsafe_allow_html=True)
            name=st.text_input('Property name or address *',value=project['name'] if project else '',max_chars=180)
            c,d=st.columns(2);c.text_input('Locality','Electronic City',disabled=True);d.text_input('City','Bengaluru',disabled=True)
            beds=c.selectbox('Bedrooms',[1,2,3,4,5],index=int(defaults.get('bedrooms',2))-1)
            size=d.number_input('Area',min_value=1.,max_value=100000.,value=float(defaults.get('area',1200.)))
            unit=c.selectbox('Unit',['sq ft','sq m'],index=0 if defaults.get('unit','sq ft')=='sq ft' else 1)
            basis=d.selectbox('Area basis',BASES,index=BASES.index(defaults.get('area_basis','Built-up')))
            notes=st.text_area('Notes (optional)',value=defaults.get('notes',''))
            names=st.multiselect('Research sources',list(SOURCES),default=['NoBroker'],max_selections=2)
            st.caption('TinyFish uses provider credits. Website access and usable evidence can vary.')
            submitted=st.form_submit_button('Start Research',type='primary',disabled=busy)
        if submitted:
            key=load_key()
            if not name.strip():st.error('Enter a property name or address.');return
            if not key:st.error('Configure TINYFISH_API_KEY in the local .env file before starting.');return
            if not names:st.error('Choose at least one source.');return
            target=Property(bedrooms=beds,area=size,unit=unit,area_basis=basis).validate()
            from dataclasses import asdict
            details=dict(asdict(target),notes=notes)
            if not project:pid=projects.create(name.strip(),details)
            else:
                with projects.connect() as db:db.execute('UPDATE projects SET name=?,details=?,updated=? WHERE id=?',(name.strip(),json.dumps(details),projects.now(),pid))
            try:manager.start(target,names,key,project_id=pid)
            except Exception:st.error('Research could not start. The property was saved; return to it and retry.');return
            navigate('property',pid)
        return
    if not project:st.warning('Property not found. Return Home to select a saved property.');return
    st.caption('HOME / PROPERTY WORKSPACE')
    image_col,info_col=st.columns([1,2.5])
    with image_col:st.markdown(cover,unsafe_allow_html=True)
    with info_col:
        st.title(project['name']);st.caption('Electronic City, Bengaluru')
        d=project['details'];st.markdown(''.join('<span class="type-chip">'+html.escape(str(v))+'</span>' for v in ['Residential apartment',str(d.get('bedrooms','—'))+' BHK',str(d.get('area','—'))+' '+d.get('unit','sq ft'),d.get('area_basis','')]),unsafe_allow_html=True)
    if st.button('Run Research Again',type='primary',disabled=busy):navigate('new',pid)
    if job and job.get('project_id')==pid:
        @st.fragment(run_every=2 if busy else None)
        def activity():
            current=manager.snapshot();render_activity(current)
            if current['state']=='running':
                if st.button('Stop research',disabled=current['stop_requested']):manager.stop();st.rerun()
            elif busy:st.rerun()
        activity()
    history=projects.runs(pid)
    overview,history_tab,manage=st.tabs(['Research & report','Research history','Manage & export'])
    with overview:
        if not history:st.info('No research runs yet.')
        else:
            chosen=st.selectbox('Research run',range(len(history)),format_func=lambda i:f"{history[i]['started'][:19]} · {history[i]['status']}")
            run=history[chosen];snapshot=run['snapshot'];report=snapshot.get('report')
            if run['status']=='running' and (not job or job['id']!=run['id']):st.warning('This saved run has no active worker in this server. It may have been interrupted. Start a new run to retry.')
            if snapshot.get('error'):st.error(snapshot['error'])
            if report:
                e=report.get('estimate')
                if e:
                    x,y,z=st.columns(3);x.metric('Indicative asking price',rupees(e['value']));y.metric('Comparison band',f"{rupees(e['low'])} – {rupees(e['high'])}");z.metric('Usable comparisons',report['accepted_count'])
                else:st.warning('Research returned insufficient evidence for an estimate.')
                for warning in report.get('warnings',[]):st.caption(warning)
                st.subheader('Comparable properties and source evidence');st.dataframe([{k:v for k,v in row.items() if k not in ('raw','warnings')} for row in report.get('records',[])],use_container_width=True)
                with st.expander('Method and source outcomes'):st.write(report.get('method'));st.json(report.get('jobs',[]))
                x,y,z=st.columns(3);x.download_button('Export Excel',workbook(project,[run]),file_name='research-run.xlsx');y.download_button('Export CSV',csv_report(report),file_name='evidence.csv');z.download_button('Download report',html_report(report),file_name='report.html')
            else:st.info('No report is available for this run yet.')
            with st.expander('Saved activity and session references'):st.json({'events':snapshot.get('events',[]),'sources':snapshot.get('sources',{})})
    with history_tab:
        st.dataframe([{'Run':r['id'],'Started':r['started'],'Status':r['status'],'Updated':r['updated']} for r in history],use_container_width=True)
    with manage:
        new_name=st.text_input('Property name',project['name'])
        if st.button('Save name'):
            if new_name.strip():projects.rename(pid,new_name.strip());st.rerun()
        st.download_button('Export Excel · all runs',workbook(project,history),file_name='property-research.xlsx')
        st.download_button('Export JSON',json.dumps({'property':project,'runs':history},indent=2),file_name='property-research.json')
        confirm=st.checkbox('I want to remove this property from my library. Its records will remain archived locally.')
        if st.button('Delete property',disabled=not confirm or busy):projects.archive(pid);navigate('home')
