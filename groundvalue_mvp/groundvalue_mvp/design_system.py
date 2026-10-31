"""
Pixel-accurate design system matching the reference screenshots.
Colors, spacing, and typography extracted from provided mockups.
"""

# Color Palette - Extracted from screenshots
COLORS = {
    # Backgrounds
    'bg_primary': '#F8FAF9',
    'bg_sidebar': '#FBFCFB',
    'bg_surface': '#FFFFFF',

    # Text
    'text_primary': '#131A25',
    'text_secondary': '#687386',
    'text_muted': '#9CA3AF',

    # Primary Green
    'primary': '#064E3B',
    'primary_hover': '#08634B',
    'primary_light': '#EAF2EF',
    'primary_soft': '#D1FAE5',

    # Borders & Dividers
    'border': '#E3E8EB',
    'border_light': '#F3F4F6',

    # Status Colors
    'status_completed': '#10B981',
    'status_in_review': '#F59E0B',
    'status_draft': '#6B7280',
    'status_error': '#EF4444',
}

# Typography
FONTS = {
    'family': '-apple-system, BlinkMacSystemFont, "Segoe UI", "Inter", "Helvetica Neue", sans-serif',
    'sizes': {
        'xs': '11px',
        'sm': '13px',
        'base': '14px',
        'lg': '16px',
        'xl': '20px',
        '2xl': '24px',
        '3xl': '30px',
        '4xl': '36px',
    },
    'weights': {
        'normal': 400,
        'medium': 500,
        'semibold': 600,
        'bold': 700,
    }
}

# Spacing (8px base unit)
SPACING = {
    'xs': '4px',
    'sm': '8px',
    'md': '12px',
    'lg': '16px',
    'xl': '24px',
    '2xl': '32px',
    '3xl': '48px',
}

# Border Radius
RADIUS = {
    'sm': '6px',
    'md': '8px',
    'lg': '10px',
    'xl': '12px',
    'full': '9999px',
}

# Shadows - Subtle, matching screenshots
SHADOWS = {
    'none': 'none',
    'sm': '0 1px 2px rgba(0, 0, 0, 0.05)',
    'base': '0 1px 3px rgba(0, 0, 0, 0.08)',
    'md': '0 2px 4px rgba(0, 0, 0, 0.06)',
    'lg': '0 4px 6px rgba(0, 0, 0, 0.07)',
}

# Layout Measurements (from screenshots)
LAYOUT = {
    'sidebar_width': '256px',
    'header_height': '72px',
    'card_gap': '20px',
    'card_padding': '20px',
    'form_max_width': '640px',
    'property_card_width': '360px',
    'property_card_image_height': '200px',
}


def get_global_styles():
    """Generate global CSS matching the reference screenshots exactly."""
    return f"""
    <style>
    /* Reset and Base Styles */
    * {{
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }}

    /* Hide Streamlit Branding */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}

    /* App Container */
    .stApp {{
        background-color: {COLORS['bg_primary']};
        font-family: {FONTS['family']};
    }}

    /* Remove Streamlit's default padding */
    .block-container {{
        padding: 2rem 3rem !important;
        max-width: 1400px !important;
    }}

    /* Sidebar Styling - Exact match to screenshots */
    [data-testid="stSidebar"] {{
        background-color: {COLORS['bg_sidebar']} !important;
        width: {LAYOUT['sidebar_width']} !important;
        border-right: 1px solid {COLORS['border']} !important;
        padding: 24px 20px !important;
    }}

    [data-testid="stSidebar"] > div:first-child {{
        padding: 0 !important;
    }}

    /* Typography */
    h1, h2, h3, h4, h5, h6 {{
        color: {COLORS['text_primary']} !important;
        font-weight: {FONTS['weights']['bold']} !important;
        line-height: 1.3 !important;
    }}

    p, span, div {{
        color: {COLORS['text_primary']};
        font-size: {FONTS['sizes']['base']};
        line-height: 1.5;
    }}

    /* Remove all Streamlit default borders and styling */
    [data-testid="stVerticalBlock"] > div {{
        border: none !important;
        background: transparent !important;
        box-shadow: none !important;
    }}

    /* Buttons */
    .stButton > button {{
        border: 1px solid {COLORS['border']} !important;
        border-radius: {RADIUS['md']} !important;
        background-color: {COLORS['bg_surface']} !important;
        color: {COLORS['text_primary']} !important;
        font-weight: {FONTS['weights']['medium']} !important;
        padding: 10px 16px !important;
        font-size: {FONTS['sizes']['sm']} !important;
        transition: all 0.15s ease !important;
        box-shadow: {SHADOWS['sm']} !important;
    }}

    .stButton > button:hover {{
        border-color: {COLORS['primary']} !important;
        background-color: {COLORS['primary_light']} !important;
        box-shadow: {SHADOWS['base']} !important;
    }}

    /* Primary Button */
    .stButton > button[kind="primary"] {{
        background-color: {COLORS['primary']} !important;
        border-color: {COLORS['primary']} !important;
        color: white !important;
        font-weight: {FONTS['weights']['semibold']} !important;
        box-shadow: {SHADOWS['md']} !important;
    }}

    .stButton > button[kind="primary"]:hover {{
        background-color: {COLORS['primary_hover']} !important;
        transform: translateY(-1px);
        box-shadow: {SHADOWS['lg']} !important;
    }}

    /* Input Fields */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div {{
        border: 1px solid {COLORS['border']} !important;
        border-radius: {RADIUS['md']} !important;
        background-color: {COLORS['bg_surface']} !important;
        color: {COLORS['text_primary']} !important;
        font-size: {FONTS['sizes']['sm']} !important;
        padding: 10px 12px !important;
        box-shadow: {SHADOWS['sm']} !important;
    }}

    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {{
        border-color: {COLORS['primary']} !important;
        box-shadow: 0 0 0 3px {COLORS['primary_light']} !important;
    }}

    /* Cards */
    .property-card {{
        background: {COLORS['bg_surface']};
        border: 1px solid {COLORS['border']};
        border-radius: {RADIUS['xl']};
        padding: 0;
        box-shadow: {SHADOWS['base']};
        transition: all 0.2s ease;
        overflow: hidden;
        height: 100%;
    }}

    .property-card:hover {{
        box-shadow: {SHADOWS['lg']};
        transform: translateY(-2px);
        border-color: {COLORS['primary_light']};
    }}

    .property-card-image {{
        width: 100%;
        height: {LAYOUT['property_card_image_height']};
        background: linear-gradient(135deg, {COLORS['primary_light']} 0%, {COLORS['bg_primary']} 100%);
        object-fit: cover;
        position: relative;
    }}

    .property-card-content {{
        padding: {LAYOUT['card_padding']};
    }}

    .property-card-title {{
        font-size: {FONTS['sizes']['lg']};
        font-weight: {FONTS['weights']['semibold']};
        color: {COLORS['text_primary']};
        margin-bottom: 8px;
    }}

    .property-card-location {{
        font-size: {FONTS['sizes']['sm']};
        color: {COLORS['text_secondary']};
        margin-bottom: 12px;
    }}

    .property-card-meta {{
        display: flex;
        gap: 16px;
        margin: 12px 0;
        font-size: {FONTS['sizes']['sm']};
        color: {COLORS['text_secondary']};
    }}

    .property-card-meta-item {{
        display: flex;
        align-items: center;
        gap: 6px;
    }}

    .property-card-divider {{
        height: 1px;
        background-color: {COLORS['border']};
        margin: 16px 0;
    }}

    .property-card-value {{
        margin-top: 12px;
    }}

    .property-card-value-label {{
        font-size: {FONTS['sizes']['xs']};
        color: {COLORS['text_muted']};
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 4px;
    }}

    .property-card-value-amount {{
        font-size: {FONTS['sizes']['2xl']};
        font-weight: {FONTS['weights']['bold']};
        color: {COLORS['text_primary']};
    }}

    .property-card-ref {{
        font-size: {FONTS['sizes']['xs']};
        color: {COLORS['text_muted']};
        margin-top: 8px;
    }}

    /* Status Badges */
    .status-badge {{
        display: inline-block;
        padding: 4px 12px;
        border-radius: {RADIUS['full']};
        font-size: {FONTS['sizes']['xs']};
        font-weight: {FONTS['weights']['medium']};
        position: absolute;
        top: 12px;
        right: 12px;
    }}

    .status-completed {{
        background-color: {COLORS['primary_soft']};
        color: {COLORS['status_completed']};
    }}

    .status-in-review {{
        background-color: #FEF3C7;
        color: {COLORS['status_in_review']};
    }}

    .status-draft {{
        background-color: #F3F4F6;
        color: {COLORS['status_draft']};
    }}

    /* Metrics */
    .metric-card {{
        background: {COLORS['bg_surface']};
        border: 1px solid {COLORS['border']};
        border-radius: {RADIUS['lg']};
        padding: 20px;
        box-shadow: {SHADOWS['sm']};
    }}

    .metric-label {{
        font-size: {FONTS['sizes']['sm']};
        color: {COLORS['text_secondary']};
        margin-bottom: 8px;
    }}

    .metric-value {{
        font-size: {FONTS['sizes']['3xl']};
        font-weight: {FONTS['weights']['bold']};
        color: {COLORS['text_primary']};
    }}

    .metric-description {{
        font-size: {FONTS['sizes']['xs']};
        color: {COLORS['text_muted']};
        margin-top: 4px;
    }}

    /* Remove Streamlit expander styling */
    .streamlit-expanderHeader {{
        border: 1px solid {COLORS['border']} !important;
        border-radius: {RADIUS['md']} !important;
        background-color: {COLORS['bg_surface']} !important;
    }}

    /* Caption styling */
    [data-testid="stCaptionContainer"] {{
        color: {COLORS['text_secondary']} !important;
        font-size: {FONTS['sizes']['sm']} !important;
    }}

    /* Divider */
    hr {{
        border: none;
        border-top: 1px solid {COLORS['border']};
        margin: 24px 0;
    }}
    </style>
    """


def sidebar_logo():
    """Return GroundValue logo SVG matching the screenshots."""
    return f"""
    <div style="padding: 16px 0 32px 0;">
        <div style="display: flex; align-items: center; gap: 12px;">
            <svg width="32" height="32" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M16 2L4 8v12c0 7.5 5.2 11.5 12 14 6.8-2.5 12-6.5 12-14V8l-12-6z"
                      fill="{COLORS['primary']}" stroke="{COLORS['primary']}" stroke-width="1.5"/>
                <path d="M11 16l3 3 7-8" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <div>
                <div style="font-size: 18px; font-weight: 700; color: {COLORS['text_primary']}; line-height: 1;">
                    GroundValue
                </div>
            </div>
        </div>
    </div>
    """


def navigation_item(label, icon, active=False, onclick=None):
    """Generate navigation item HTML."""
    bg = COLORS['primary_light'] if active else 'transparent'
    color = COLORS['primary'] if active else COLORS['text_secondary']
    weight = FONTS['weights']['semibold'] if active else FONTS['weights']['normal']

    return f"""
    <div style="
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 12px 16px;
        margin: 4px 0;
        border-radius: {RADIUS['md']};
        background-color: {bg};
        color: {color};
        font-weight: {weight};
        font-size: {FONTS['sizes']['sm']};
        cursor: pointer;
        transition: all 0.15s ease;
    ">
        <span style="font-size: 18px;">{icon}</span>
        <span>{label}</span>
    </div>
    """
