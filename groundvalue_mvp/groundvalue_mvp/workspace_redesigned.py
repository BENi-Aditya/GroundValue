"""
Property Workspace UI matching Reference Screenshot 3.
Clean, professional layout with Overview/History/Export tabs.
"""
import json
import streamlit as st
from design_system import COLORS, FONTS, RADIUS, SHADOWS, SPACING
from report import rupees, csv_report, html_report
from excel_export import workbook
from progress_ui import render_activity


def workspace_redesigned(project, manager, dark):
    """Render property workspace matching Reference Screenshot 3."""
    from application_redesigned import navigate
    import projects

    pid = project['id']
    details = json.loads(project['details'])
    history = projects.runs(pid)

    # Header with back button and actions
    st.markdown(f"""
    <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 24px;">
        <div>
            <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 8px;">
                <span style="font-size: 24px; cursor: pointer;">←</span>
                <h1 style="font-size: {FONTS['sizes']['3xl']}; margin: 0;">{project['name']}</h1>
            </div>
            <p style="color: {COLORS['text_secondary']}; font-size: {FONTS['sizes']['sm']}; margin: 0;">
                Whitefield, Bengaluru, Karnataka • Ref: GV-2024-0012
            </p>
        </div>
        <div style="display: flex; gap: 12px;">
            <button style="
                padding: 10px 16px;
                border: 1px solid {COLORS['border']};
                border-radius: {RADIUS['md']};
                background: {COLORS['bg_surface']};
                color: {COLORS['text_primary']};
                font-size: {FONTS['sizes']['sm']};
                font-weight: {FONTS['weights']['medium']};
                cursor: pointer;
            ">✏️ Edit</button>
            <button style="
                padding: 10px 16px;
                border: 1px solid {COLORS['border']};
                border-radius: {RADIUS['md']};
                background: {COLORS['primary']};
                color: white;
                font-size: {FONTS['sizes']['sm']};
                font-weight: {FONTS['weights']['medium']};
                cursor: pointer;
            ">📤 Export</button>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Back button functionality
    col_back, col_edit, col_export = st.columns([6, 1, 1])
    with col_back:
        if st.button('← Back', key='back_to_dashboard'):
            navigate('home')
    with col_edit:
        if st.button('✏️ Edit', key='edit_property', use_container_width=True):
            navigate('new', pid)
    with col_export:
        st.session_state['show_export_modal'] = st.button('📤 Export', key='export_property', use_container_width=True)

    # Tab Navigation
    tab1, tab2, tab3 = st.tabs(['Overview', 'History', 'Export'])

    with tab1:
        render_overview_tab(project, history, manager, dark)

    with tab2:
        render_history_tab(project, history, manager)

    with tab3:
        render_export_tab(project, history, dark)


def render_overview_tab(project, history, manager, dark):
    """Render Overview tab with metrics and property details."""
    details = json.loads(project['details'])

    # Three metric cards at the top
    if history:
        latest = history[0]
        snapshot = latest['snapshot']
        report = snapshot.get('report', {})
        estimate = report.get('estimate')
        comparisons = report.get('comparisons', [])

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div style="margin-bottom: 8px;">
                    <span style="font-size: 20px;">●</span>
                    <span style="margin-left: 8px; color: {COLORS['text_secondary']}; font-size: {FONTS['sizes']['sm']};">Status</span>
                </div>
                <div class="metric-value">{latest['status'].title()}</div>
                <div class="metric-description">Research completed successfully</div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            value_display = rupees(estimate['value']) if estimate else 'Not estimated'
            st.markdown(f"""
            <div class="metric-card">
                <div style="margin-bottom: 8px;">
                    <span style="font-size: 20px;">₹</span>
                    <span style="margin-left: 8px; color: {COLORS['text_secondary']}; font-size: {FONTS['sizes']['sm']};">Estimated Value</span>
                </div>
                <div class="metric-value">{value_display}</div>
                <div class="metric-description">As on {latest.get('started', '')[:10]}</div>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <div style="margin-bottom: 8px;">
                    <span style="font-size: 20px;">📋</span>
                    <span style="margin-left: 8px; color: {COLORS['text_secondary']}; font-size: {FONTS['sizes']['sm']};">Comps</span>
                </div>
                <div class="metric-value">{len(comparisons)}</div>
                <div class="metric-description">Comparable properties analysed</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info('📊 No research runs yet for this property')

    st.markdown('<div style="height: 32px;"></div>', unsafe_allow_html=True)

    # Two-column layout: Property Details + Property Summary
    col_left, col_right = st.columns([1.4, 1])

    with col_left:
        # Property Details Card
        st.markdown(f"""
        <div style="
            background: {COLORS['bg_surface']};
            border: 1px solid {COLORS['border']};
            border-radius: {RADIUS['xl']};
            padding: 24px;
            box-shadow: {SHADOWS['base']};
        ">
            <h3 style="font-size: {FONTS['sizes']['xl']}; margin-bottom: 20px;">Property Details</h3>
        """, unsafe_allow_html=True)

        # Detail rows
        detail_items = [
            ('📍', 'Location', 'Whitefield, Bengaluru, Karnataka', 'View on Map'),
            ('🏢', 'Property Type', 'Apartment', None),
            ('📐', 'Built-up Area', f"{details.get('area', 0)} sq ft", None),
            ('📏', 'Basis', details.get('area_basis', 'Built-up'), None),
            ('📝', 'Notes', details.get('notes', 'Premium residential project with good connectivity and social infrastructure.'), None),
        ]

        for icon, label, value, action in detail_items:
            st.markdown(f"""
            <div style="
                display: flex;
                padding: 16px 0;
                border-bottom: 1px solid {COLORS['border_light']};
            ">
                <div style="width: 40px; font-size: 20px;">{icon}</div>
                <div style="flex: 1;">
                    <div style="color: {COLORS['text_secondary']}; font-size: {FONTS['sizes']['sm']}; margin-bottom: 4px;">{label}</div>
                    <div style="color: {COLORS['text_primary']}; font-size: {FONTS['sizes']['base']};">{value}</div>
                </div>
                {'<div style="color: ' + COLORS['primary'] + '; font-size: ' + FONTS['sizes']['sm'] + '; cursor: pointer;">' + action + ' →</div>' if action else ''}
            </div>
            """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

        # Action buttons
        st.markdown('<div style="height: 20px;"></div>', unsafe_allow_html=True)
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button('+ New Research', type='primary', use_container_width=True, key='new_research_overview'):
                from research import SOURCES
                from tinyfish_client import load_key
                key = load_key()
                if key:
                    sources = ['NoBroker']
                    manager.start(project['id'], sources, key)
                    st.rerun()
        with col_btn2:
            if st.button('View Details', use_container_width=True, key='view_details_overview'):
                pass  # Expand details

    with col_right:
        # Property Summary Card
        st.markdown(f"""
        <div style="
            background: {COLORS['bg_surface']};
            border: 1px solid {COLORS['border']};
            border-radius: {RADIUS['xl']};
            padding: 24px;
            box-shadow: {SHADOWS['base']};
        ">
            <h3 style="font-size: {FONTS['sizes']['xl']}; margin-bottom: 20px;">Property Summary</h3>
        """, unsafe_allow_html=True)

        # Property image placeholder
        st.markdown(f"""
        <div style="
            width: 100%;
            height: 200px;
            background: linear-gradient(135deg, {COLORS['primary_light']} 0%, {COLORS['bg_primary']} 100%);
            border-radius: {RADIUS['lg']};
            display: flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 20px;
        ">
            <svg width="100" height="80" viewBox="0 0 100 80" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M50 5 L5 25 L5 70 L95 70 L95 25 Z" stroke="{COLORS['primary']}" stroke-width="2" fill="{COLORS['primary_light']}"/>
                <rect x="38" y="35" width="24" height="35" fill="{COLORS['primary']}" opacity="0.3"/>
            </svg>
        </div>
        """, unsafe_allow_html=True)

        # Property info
        st.markdown(f"""
        <div style="margin-bottom: 16px;">
            <h4 style="font-size: {FONTS['sizes']['lg']}; margin-bottom: 8px;">{project['name']}</h4>
            <p style="color: {COLORS['text_secondary']}; font-size: {FONTS['sizes']['sm']}; margin-bottom: 12px;">
                Whitefield, Bengaluru, Karnataka
            </p>
            <div style="display: flex; gap: 16px; margin-bottom: 16px;">
                <span style="color: {COLORS['text_secondary']}; font-size: {FONTS['sizes']['sm']};">🏢 Apartment</span>
                <span style="color: {COLORS['text_secondary']}; font-size: {FONTS['sizes']['sm']};">📐 {details.get('area', 0)} sq ft</span>
                <span style="color: {COLORS['text_secondary']}; font-size: {FONTS['sizes']['sm']};">🛏️ {details.get('bedrooms', 0)} BHK</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Source Summary
        if history:
            latest = history[0]
            sources = latest['snapshot'].get('sources', {})
            st.markdown(f"""
            <div style="border-top: 1px solid {COLORS['border']}; padding-top: 16px; margin-top: 16px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                    <h4 style="font-size: {FONTS['sizes']['base']}; margin: 0;">Source Summary</h4>
                    <a href="#" style="color: {COLORS['primary']}; font-size: {FONTS['sizes']['sm']}; text-decoration: none;">View Sources →</a>
                </div>
                <div style="display: flex; gap: 24px;">
                    <div style="flex: 1;">
                        <div style="font-size: {FONTS['sizes']['2xl']}; font-weight: {FONTS['weights']['bold']}; color: {COLORS['text_primary']};">12</div>
                        <div style="font-size: {FONTS['sizes']['xs']}; color: {COLORS['text_muted']};">Listings</div>
                    </div>
                    <div style="flex: 1;">
                        <div style="font-size: {FONTS['sizes']['2xl']}; font-weight: {FONTS['weights']['bold']}; color: {COLORS['text_primary']};">5</div>
                        <div style="font-size: {FONTS['sizes']['xs']}; color: {COLORS['text_muted']};">Transactions</div>
                    </div>
                    <div style="flex: 1;">
                        <div style="font-size: {FONTS['sizes']['2xl']}; font-weight: {FONTS['weights']['bold']}; color: {COLORS['text_primary']};">3</div>
                        <div style="font-size: {FONTS['sizes']['xs']}; color: {COLORS['text_muted']};">Reports</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Latest Valuation Snapshot
            report = latest['snapshot'].get('report', {})
            estimate = report.get('estimate')
            if estimate:
                st.markdown(f"""
                <div style="border-top: 1px solid {COLORS['border']}; padding-top: 16px; margin-top: 16px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                        <h4 style="font-size: {FONTS['sizes']['base']}; margin: 0;">Latest Valuation Snapshot</h4>
                        <span style="color: {COLORS['text_muted']}; font-size: {FONTS['sizes']['xs']};">{latest.get('started', '')[:10]}</span>
                    </div>
                    <div style="font-size: {FONTS['sizes']['3xl']}; font-weight: {FONTS['weights']['bold']}; color: {COLORS['text_primary']}; margin-bottom: 4px;">
                        {rupees(estimate['value'])}
                    </div>
                    <div style="font-size: {FONTS['sizes']['sm']}; color: {COLORS['text_secondary']};">
                        Value range: {rupees(estimate.get('min_value', 0))} – {rupees(estimate.get('max_value', 0))}
                    </div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    # Research History Section
    st.markdown(f'<div style="height: 32px;"></div>', unsafe_allow_html=True)
    st.markdown(f'<h3 style="font-size: {FONTS["sizes"]["xl"]}; margin-bottom: 16px;">Research History</h3>', unsafe_allow_html=True)

    if history:
        for idx, run in enumerate(history[:5]):
            status_colors = {
                'completed': COLORS['status_completed'],
                'running': COLORS['status_in_review'],
                'failed': COLORS['status_error']
            }
            status_color = status_colors.get(run['status'], COLORS['text_muted'])

            st.markdown(f"""
            <div style="
                background: {COLORS['bg_surface']};
                border: 1px solid {COLORS['border']};
                border-radius: {RADIUS['lg']};
                padding: 16px 20px;
                margin-bottom: 12px;
                display: flex;
                justify-content: space-between;
                align-items: center;
                cursor: pointer;
            ">
                <div>
                    <div style="font-size: {FONTS['sizes']['base']}; font-weight: {FONTS['weights']['medium']}; margin-bottom: 4px;">
                        {run.get('started', '')[:19].replace('T', ' ')} — Market analysis with updated comps
                    </div>
                    <div style="font-size: {FONTS['sizes']['sm']}; color: {COLORS['text_secondary']};">
                        <span style="color: {status_color}; margin-right: 8px;">●</span> {run['status'].title()}
                    </div>
                </div>
                <div style="color: {COLORS['primary']};">→</div>
            </div>
            """, unsafe_allow_html=True)


def render_history_tab(project, history, manager):
    """Render History tab with all research runs."""
    st.markdown(f'<h3 style="font-size: {FONTS["sizes"]["xl"]}; margin-bottom: 20px;">Research History</h3>', unsafe_allow_html=True)

    if not history:
        st.info('📋 No research runs yet for this property')
        return

    for idx, run in enumerate(history):
        with st.expander(f"Run #{len(history) - idx} — {run.get('started', '')[:10]} — {run['status'].title()}", expanded=(idx == 0)):
            snapshot = run['snapshot']
            report = snapshot.get('report', {})

            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Started:** {run.get('started', '')}")
                if run.get('finished'):
                    st.write(f"**Finished:** {run.get('finished', '')}")
            with col2:
                st.write(f"**Status:** {run['status'].title()}")
                sources = snapshot.get('sources', {})
                st.write(f"**Sources:** {len(sources)}")

            if report:
                estimate = report.get('estimate')
                if estimate:
                    st.success(f"**Estimated Value:** {rupees(estimate['value'])}")

                comparisons = report.get('comparisons', [])
                st.write(f"**Comparisons Found:** {len(comparisons)}")

                if comparisons:
                    st.markdown('#### Sample Comparisons')
                    for comp in comparisons[:5]:
                        st.write(f"- {comp.get('bedrooms')} BHK, {comp.get('area')} sq ft — ₹{comp.get('price', 0):,.0f}")


def render_export_tab(project, history, dark):
    """Render Export tab."""
    st.markdown(f'<h3 style="font-size: {FONTS["sizes"]["xl"]}; margin-bottom: 20px;">Export Reports</h3>', unsafe_allow_html=True)

    if not history or history[0]['status'] != 'completed':
        st.warning('⚠️ Complete a research run to generate export reports')
        return

    latest = history[0]
    report = latest['snapshot'].get('report', {})

    st.write('Export your property research data in multiple formats:')
    st.markdown('<div style="height: 20px;"></div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f'<h4 style="font-size: {FONTS["sizes"]["lg"]};">📊 CSV</h4>', unsafe_allow_html=True)
        st.caption('Spreadsheet format for analysis')
        csv_data = csv_report(report)
        st.download_button(
            '⬇️ Download CSV',
            csv_data,
            file_name=f"groundvalue_{project['name'].replace(' ', '_')}.csv",
            mime='text/csv',
            use_container_width=True,
            type='primary'
        )

    with col2:
        st.markdown(f'<h4 style="font-size: {FONTS["sizes"]["lg"]};">📄 HTML</h4>', unsafe_allow_html=True)
        st.caption('Readable web format')
        html_data = html_report(project, report, dark)
        st.download_button(
            '⬇️ Download HTML',
            html_data,
            file_name=f"groundvalue_{project['name'].replace(' ', '_')}.html",
            mime='text/html',
            use_container_width=True,
            type='primary'
        )

    with col3:
        st.markdown(f'<h4 style="font-size: {FONTS["sizes"]["lg"]};">📗 Excel</h4>', unsafe_allow_html=True)
        st.caption('Full data with multiple sheets')
        excel_data = workbook(project, report)
        st.download_button(
            '⬇️ Download Excel',
            excel_data,
            file_name=f"groundvalue_{project['name'].replace(' ', '_')}.xlsx",
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            use_container_width=True,
            type='primary'
        )
