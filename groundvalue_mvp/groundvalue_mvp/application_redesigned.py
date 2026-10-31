"""
Redesigned application matching reference screenshots pixel-accurately.
Preserves all existing functionality while updating visual design.
"""
import json
import streamlit as st
import projects
from design_system import get_global_styles, sidebar_logo, navigation_item, COLORS, FONTS, SPACING, RADIUS, SHADOWS
from core import Property, BASES
from jobs import get_manager
from tinyfish_client import load_key
from research import SOURCES
from progress_ui import render_activity
from report import rupees, csv_report, html_report
from excel_export import workbook


def navigate(page, pid=None):
    """Navigate between pages."""
    st.query_params['page'] = page
    if pid:
        st.query_params['property'] = pid
    elif 'property' in st.query_params:
        del st.query_params['property']
    st.rerun()


def render_sidebar(page):
    """Render sidebar with clean navigation matching screenshot."""
    with st.sidebar:
        # Logo
        st.markdown(sidebar_logo(), unsafe_allow_html=True)

        # Navigation
        st.markdown(navigation_item('Dashboard', '🏠', active=(page == 'home')), unsafe_allow_html=True)
        if st.button('Dashboard', key='nav_dashboard', use_container_width=True,
                     type='primary' if page == 'home' else 'secondary'):
            navigate('home')

        st.markdown(navigation_item('New Research', '📋', active=(page == 'new')), unsafe_allow_html=True)
        if st.button('New Research', key='nav_new_research', use_container_width=True,
                     type='primary' if page == 'new' else 'secondary'):
            navigate('new')

        # Spacer
        st.markdown('<div style="flex: 1; min-height: 200px;"></div>', unsafe_allow_html=True)

        # Theme toggle at bottom
        st.markdown('<div style="padding-top: 24px; border-top: 1px solid #E3E8EB;"></div>', unsafe_allow_html=True)
        theme_icon = '🌙' if not st.session_state.get('app_dark', False) else '☀️'
        if st.button(f'{theme_icon} Light mode', key='theme_toggle', use_container_width=True):
            st.session_state.app_dark = not st.session_state.get('app_dark', False)
            st.rerun()


def render_property_card(project, history, ref_id):
    """Render a single property card matching screenshot design."""
    details = json.loads(project['details'])
    state = history[0]['status'] if history else 'draft'

    # Get valuation
    result = (history[0]['snapshot'].get('report') or {}) if history else {}
    estimate = result.get('estimate')

    # Status badge color
    status_class = {
        'completed': 'status-completed',
        'running': 'status-in-review',
        'draft': 'status-draft',
        'failed': 'status-draft'
    }.get(state, 'status-draft')

    status_label = {
        'completed': 'Completed',
        'running': 'In Review',
        'draft': 'Draft',
        'failed': 'Draft'
    }.get(state, 'Draft')

    # Card HTML
    card_html = f"""
    <div class="property-card">
        <div class="property-card-image">
            <div class="status-badge {status_class}">{status_label}</div>
            <div style="display: flex; align-items: center; justify-content: center; height: 100%; padding: 40px;">
                <svg width="120" height="100" viewBox="0 0 120 100" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M60 10 L10 35 L10 85 L110 85 L110 35 Z" stroke="{COLORS['primary']}" stroke-width="2" fill="{COLORS['primary_light']}"/>
                    <rect x="45" y="50" width="30" height="35" fill="{COLORS['primary']}" opacity="0.3"/>
                    <rect x="25" y="45" width="15" height="15" fill="{COLORS['primary']}" opacity="0.3"/>
                    <rect x="80" y="45" width="15" height="15" fill="{COLORS['primary']}" opacity="0.3"/>
                </svg>
            </div>
        </div>
        <div class="property-card-content">
            <div class="property-card-title">{project['name']}</div>
            <div class="property-card-location">📍 Electronic City, Bengaluru, Karnataka</div>

            <div class="property-card-meta">
                <div class="property-card-meta-item">
                    <span>🏢</span> Apartment
                </div>
                <div class="property-card-meta-item">
                    <span>📐</span> {details.get('area', 0)} sq ft
                </div>
                <div class="property-card-meta-item">
                    <span>🛏️</span> {details.get('bedrooms', 0)} BHK
                </div>
            </div>

            <div class="property-card-divider"></div>

            <div class="property-card-value">
                <div class="property-card-value-label">Estimated Value</div>
                <div class="property-card-value-amount">
                    {rupees(estimate['value']) if estimate else '—'}
                </div>
                <div class="property-card-ref">Ref: {ref_id}</div>
            </div>
        </div>
    </div>
    """

    st.markdown(card_html, unsafe_allow_html=True)

    # View button below card
    if st.button('View', key=f'view_{project["id"]}', use_container_width=True):
        navigate('property', project['id'])


def render_dashboard():
    """Render Dashboard page matching Reference Screenshot 1."""
    # Header
    col1, col2 = st.columns([6, 1])
    with col1:
        st.markdown(f'<h1 style="font-size: {FONTS["sizes"]["4xl"]}; margin-bottom: 8px;">Properties</h1>', unsafe_allow_html=True)
        st.markdown(f'<p style="color: {COLORS["text_secondary"]}; font-size: {FONTS["sizes"]["base"]};">Search, analyze and manage property research and valuations across India.</p>', unsafe_allow_html=True)

    with col2:
        if st.button('+ New Research', type='primary', use_container_width=True):
            navigate('new')

    st.markdown(f'<div style="height: 32px;"></div>', unsafe_allow_html=True)

    # Search and Filters Row
    col_search, col_city, col_type, col_status = st.columns([3, 1, 1, 1])

    with col_search:
        search = st.text_input(
            'Search',
            placeholder='Search by property name, location or reference ID...',
            label_visibility='collapsed'
        )

    with col_city:
        city_filter = st.selectbox('City', ['All Cities'], label_visibility='collapsed')

    with col_type:
        type_filter = st.selectbox('Property Type', ['All Property Types'], label_visibility='collapsed')

    with col_status:
        status_filter = st.selectbox('Status', ['All Status'], label_visibility='collapsed')

    st.markdown(f'<div style="height: 32px;"></div>', unsafe_allow_html=True)

    # Property Cards Grid (3 columns)
    items = projects.listing()

    if not items:
        st.info('🏢 No properties yet. Create your first property to start research.')
        return

    # Filter by search
    if search:
        items = [p for p in items if search.lower() in (p['name'] + p['details']).lower()]

    # Render in 3-column grid
    for start in range(0, len(items), 3):
        cols = st.columns(3)
        for idx, project in enumerate(items[start:start+3]):
            with cols[idx]:
                history = projects.runs(project['id'])
                ref_id = f"GV-2024-{str(start + idx + 1).zfill(4)}"
                render_property_card(project, history, ref_id)


def render_new_research():
    """Render New Research page matching Reference Screenshot 2."""
    # Breadcrumb and Title
    st.markdown(f'<p style="color: {COLORS["text_muted"]}; font-size: {FONTS["sizes"]["sm"]}; margin-bottom: 8px;">Dashboard > New Research</p>', unsafe_allow_html=True)
    st.markdown(f'<h1 style="font-size: {FONTS["sizes"]["4xl"]}; margin-bottom: 8px;">Create Property Research</h1>', unsafe_allow_html=True)
    st.markdown(f'<p style="color: {COLORS["text_secondary"]}; font-size: {FONTS["sizes"]["base"]}; margin-bottom: 32px;">Run a comprehensive property research and valuation using multiple data sources across India.</p>', unsafe_allow_html=True)

    # Two-column layout
    col_form, col_info = st.columns([1.65, 1])

    with col_form:
        # Property Details Form
        st.markdown(f'<h2 style="font-size: {FONTS["sizes"]["xl"]}; margin-bottom: 20px;">Property Details</h2>', unsafe_allow_html=True)

        with st.form('property_form'):
            # Property Name
            name = st.text_input(
                'Property Name',
                placeholder='e.g. Prestige Lakeside Homes, Sobha Forest Edge'
            )

            # Location (Fixed to Electronic City for MVP)
            location = st.text_input(
                'Location',
                value='Electronic City, Bengaluru',
                disabled=True,
                help='Currently available in Electronic City, Bengaluru only'
            )

            # Bedrooms and Area
            col_bed, col_area = st.columns(2)
            with col_bed:
                bedrooms = st.selectbox('Bedrooms', ['Select bedrooms', '1', '2', '3', '4', '5'])
            with col_area:
                area = st.number_input('Area (sq ft)', min_value=100, max_value=10000, value=1200, step=50)

            # Unit and Basis
            col_unit, col_basis = st.columns(2)
            with col_unit:
                unit = st.selectbox('Unit', ['Select unit', 'sq ft', 'sq m'])
            with col_basis:
                basis = st.selectbox('Basis', ['Select basis'] + BASES)

            # Notes
            notes = st.text_area(
                'Notes (Optional)',
                placeholder='Add any specific details, preferences or context for this research...',
                height=100
            )

            st.markdown('<div style="height: 24px;"></div>', unsafe_allow_html=True)

            # Sources Section
            st.markdown(f'<h3 style="font-size: {FONTS["sizes"]["lg"]}; margin-bottom: 16px;">Sources</h3>', unsafe_allow_html=True)
            st.markdown(f'<p style="color: {COLORS["text_secondary"]}; font-size: {FONTS["sizes"]["sm"]}; margin-bottom: 16px;">Select up to 2 sources for this research.</p>', unsafe_allow_html=True)

            # Source checkboxes
            sources = st.multiselect(
                'Data Sources',
                list(SOURCES.keys()),
                default=[],
                max_selections=2,
                label_visibility='collapsed'
            )

            st.markdown('<div style="height: 24px;"></div>', unsafe_allow_html=True)

            # Submit Button
            submitted = st.form_submit_button(
                'Start Research',
                type='primary',
                use_container_width=True
            )

        if submitted:
            # Validation
            if not name or name.strip() == '':
                st.error('❌ Please enter a property name')
            elif bedrooms == 'Select bedrooms':
                st.error('❌ Please select number of bedrooms')
            elif unit == 'Select unit':
                st.error('❌ Please select unit')
            elif basis == 'Select basis':
                st.error('❌ Please select area basis')
            elif not sources:
                st.error('❌ Please select at least one data source')
            else:
                # Create property and start research
                key = load_key()
                if not key:
                    st.error('❌ TINYFISH_API_KEY not configured in .env file')
                else:
                    details = {
                        'bedrooms': int(bedrooms),
                        'area': area,
                        'unit': unit,
                        'area_basis': basis,
                        'notes': notes
                    }
                    pid = projects.create(name, details)
                    manager = get_manager()
                    manager.start(pid, sources, key)
                    navigate('property', pid)

    with col_info:
        # Information Panel
        st.markdown(f"""
        <div style="
            background: {COLORS['bg_surface']};
            border: 1px solid {COLORS['border']};
            border-radius: {RADIUS['lg']};
            padding: 24px;
            margin-bottom: 20px;
        ">
            <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 16px;">
                <div style="
                    width: 40px;
                    height: 40px;
                    border-radius: {RADIUS['md']};
                    background: {COLORS['primary_light']};
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 20px;
                ">📍</div>
                <div>
                    <h3 style="font-size: {FONTS['sizes']['lg']}; font-weight: {FONTS['weights']['semibold']}; margin: 0;">India-wide coverage</h3>
                </div>
            </div>
            <p style="color: {COLORS['text_secondary']}; font-size: {FONTS['sizes']['sm']}; line-height: 1.6; margin: 0;">
                Residential and commercial properties across major cities and towns in India.
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style="
            background: {COLORS['bg_surface']};
            border: 1px solid {COLORS['border']};
            border-radius: {RADIUS['lg']};
            padding: 24px;
            margin-bottom: 20px;
        ">
            <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 16px;">
                <div style="
                    width: 40px;
                    height: 40px;
                    border-radius: {RADIUS['md']};
                    background: {COLORS['primary_light']};
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 20px;
                ">💾</div>
                <div>
                    <h3 style="font-size: {FONTS['sizes']['lg']}; font-weight: {FONTS['weights']['semibold']}; margin: 0;">Multiple data sources</h3>
                </div>
            </div>
            <p style="color: {COLORS['text_secondary']}; font-size: {FONTS['sizes']['sm']}; line-height: 1.6; margin: 0;">
                Combine data from transaction portals, government records, maps and builder listings for a comprehensive view.
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style="
            background: {COLORS['bg_surface']};
            border: 1px solid {COLORS['border']};
            border-radius: {RADIUS['lg']};
            padding: 24px;
        ">
            <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 16px;">
                <div style="
                    width: 40px;
                    height: 40px;
                    border-radius: {RADIUS['md']};
                    background: {COLORS['primary_light']};
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 20px;
                ">📊</div>
                <div>
                    <h3 style="font-size: {FONTS['sizes']['lg']}; font-weight: {FONTS['weights']['semibold']}; margin: 0;">What you'll get</h3>
                </div>
            </div>
            <p style="color: {COLORS['text_secondary']}; font-size: {FONTS['sizes']['sm']}; margin-bottom: 12px;">
                A single research run will collect and analyze:
            </p>
            <ul style="color: {COLORS['text_secondary']}; font-size: {FONTS['sizes']['sm']}; line-height: 1.8; margin: 0; padding-left: 20px;">
                <li>Recent transaction data and price trends</li>
                <li>Property and project details</li>
                <li>Location and locality insights</li>
                <li>Comparative market analysis</li>
                <li>Estimated property value range</li>
                <li>Key insights and recommendations</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)


def render():
    """Main render function."""
    # Import legacy data
    projects.import_legacy()

    # Initialize session state
    if 'app_dark' not in st.session_state:
        st.session_state.app_dark = False

    # Get current page
    page = st.query_params.get('page', 'home')

    # Inject global styles
    st.markdown(get_global_styles(), unsafe_allow_html=True)

    # Render sidebar
    render_sidebar(page)

    # Render page content
    if page == 'home':
        render_dashboard()
    elif page == 'new':
        render_new_research()
    elif page == 'property':
        # Property workspace - will implement next
        pid = st.query_params.get('property')
        project = projects.get(pid) if pid else None
        if project:
            from workspace_redesigned import workspace_redesigned
            manager = get_manager()
            workspace_redesigned(project, manager, st.session_state.app_dark)
        else:
            st.error('Property not found')
            if st.button('← Back to Dashboard'):
                navigate('home')
