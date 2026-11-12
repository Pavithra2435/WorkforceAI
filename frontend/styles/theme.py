"""
================================================================================
Design System & Theme Engine for WorkforceAI Dashboard
Color Theory (60-30-10 Rule):
  - 60% Dominant Canvas: Pure White (#FFFFFF) & Soft Canvas (#F8FAFC)
  - 30% Structural Neutrals: Deep Slate Charcoal (#0F172A, #334155, #E2E8F0)
  - 10% Intentional Accent: Terracotta / Rust Orange (#C2410C) & Amber (#FFF7ED)
Professional Enterprise UI: Vector SVG iconography, zero emojis, full responsiveness.
================================================================================
"""

import plotly.graph_objects as go

# ------------------------------------------------------------------------------
# 1. CORE COLOR PALETTE CONSTANTS
# ------------------------------------------------------------------------------
COLOR_PRIMARY = "#C2410C"          # Rust Orange / Terracotta Accent
COLOR_PRIMARY_LIGHT = "#FFF7ED"    # Soft Amber / Orange Wash
COLOR_PRIMARY_BORDER = "#FED7AA"   # Warm Amber Border
COLOR_PRIMARY_DARK = "#9A3412"     # Deep Terracotta

COLOR_CANVAS = "#F8FAFC"           # Clean Neutral Canvas
COLOR_CARD_BG = "#FFFFFF"          # Pure White Surfaces
COLOR_BORDER = "#E2E8F0"           # Hairline Slate Border
COLOR_BORDER_STRONG = "#CBD5E1"    # Structural Slate Border

COLOR_TEXT_DARK = "#0F172A"        # Slate 900 for Primary Typography
COLOR_TEXT_BODY = "#334155"        # Slate 700 for High-Contrast Body
COLOR_TEXT_MUTED = "#64748B"       # Slate 500 for Secondary Subtitles

COLOR_SUCCESS = "#059669"          # Emerald Green
COLOR_WARNING = "#D97706"          # Warm Amber
COLOR_DANGER = "#DC2626"           # Crimson Red
COLOR_INFO = "#0284C7"             # Sky Blue

# ------------------------------------------------------------------------------
# 2. GLOBAL RESPONSIVE CSS INJECTION STRING
# ------------------------------------------------------------------------------
GLOBAL_CUSTOM_CSS = f"""
<style>
    /* =========================================================================
       1. STREAMLIT ZERO-HEIGHT HEADER & SIDEBAR CONTROLS
       ========================================================================= */
    header[data-testid="stHeader"] {{
        background-color: transparent !important;
        height: 0px !important;
        min-height: 0px !important;
        max-height: 0px !important;
        padding: 0 !important;
        margin: 0 !important;
        z-index: 9999 !important;
        pointer-events: none !important;
        overflow: visible !important;
        border: none !important;
    }}
    
    /* Ensure sidebar expand / collapse controls are ALWAYS clickable and prominent */
    header[data-testid="stHeader"] button,
    [data-testid="collapsedControl"],
    [data-testid="stSidebarCollapsedControl"],
    button[data-testid="stSidebarCollapseButton"] {{
        pointer-events: auto !important;
        visibility: visible !important;
        display: flex !important;
        opacity: 1 !important;
        z-index: 100000 !important;
        color: {COLOR_PRIMARY} !important;
    }}
    
    /* Prominent Sidebar Expand Button (visible when sidebar is collapsed) */
    [data-testid="collapsedControl"],
    [data-testid="stSidebarCollapsedControl"] {{
        position: fixed !important;
        top: 10px !important;
        left: 10px !important;
        display: flex !important;
        visibility: visible !important;
        opacity: 1 !important;
        z-index: 999999 !important;
    }}
    
    [data-testid="collapsedControl"] button,
    [data-testid="stSidebarCollapsedControl"] button {{
        background-color: #FFFFFF !important;
        border: 1.5px solid {COLOR_PRIMARY} !important;
        color: {COLOR_PRIMARY} !important;
        border-radius: 8px !important;
        padding: 0.4rem 0.75rem !important;
        box-shadow: 0 4px 12px rgba(194, 65, 12, 0.22) !important;
        cursor: pointer !important;
        transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1) !important;
    }}
    
    [data-testid="collapsedControl"] button:hover,
    [data-testid="stSidebarCollapsedControl"] button:hover {{
        background-color: {COLOR_PRIMARY_LIGHT} !important;
        transform: scale(1.05) !important;
        box-shadow: 0 6px 16px rgba(194, 65, 12, 0.3) !important;
    }}

    /* Hide default Streamlit fluff */
    #MainMenu {{ display: none !important; }}
    footer {{ display: none !important; }}
    div[data-testid="stToolbar"] {{ display: none !important; }}
    div[data-testid="stDecoration"] {{ display: none !important; }}
    div[data-testid="stStatusWidget"] {{ display: none !important; }}
    
    /* =========================================================================
       2. CANVAS & ZERO-GAP TOP SPACING
       ========================================================================= */
    html, body, [data-testid="stAppViewContainer"] {{
        background-color: {COLOR_CANVAS} !important;
        color: {COLOR_TEXT_DARK} !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        overflow-x: hidden !important;
    }}
    
    [data-testid="stAppViewContainer"] > .main {{
        padding-top: 0 !important;
    }}

    .main .block-container {{
        padding-top: 0.35rem !important;
        padding-bottom: 2rem !important;
        padding-left: 1.25rem !important;
        padding-right: 1.25rem !important;
        max-width: 100% !important;
    }}

    /* =========================================================================
       3. SIDEBAR STYLING & ANIMATION
       ========================================================================= */
    [data-testid="stSidebar"] {{
        background-color: #FFFFFF !important;
        border-right: 1px solid {COLOR_BORDER} !important;
        box-shadow: 2px 0 10px rgba(0, 0, 0, 0.03) !important;
        transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1), width 0.3s ease !important;
    }}

    [data-testid="stSidebar"] > div:first-child {{
        padding-top: 1rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }}

    /* Brand Header Box */
    .brand-box {{
        display: flex;
        align-items: center;
        gap: 0.65rem;
        padding-bottom: 0.85rem;
        margin-bottom: 0.85rem;
        border-bottom: 1px solid {COLOR_BORDER};
    }}

    .brand-logo {{
        width: 34px;
        height: 34px;
        border-radius: 8px;
        background: linear-gradient(135deg, {COLOR_PRIMARY} 0%, {COLOR_PRIMARY_DARK} 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        color: #FFFFFF;
        font-weight: 800;
        font-size: 1.05rem;
        letter-spacing: -0.02em;
        box-shadow: 0 2px 6px rgba(194, 65, 12, 0.3);
    }}

    .brand-title {{
        font-size: 1.05rem;
        font-weight: 800;
        color: {COLOR_TEXT_DARK};
        letter-spacing: -0.02em;
        line-height: 1.2;
    }}

    .brand-sub {{
        font-size: 0.72rem;
        font-weight: 600;
        color: {COLOR_TEXT_MUTED};
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }}

    /* Sidebar Status Badge */
    .status-badge {{
        display: inline-flex;
        align-items: center;
        gap: 0.45rem;
        background-color: #ECFDF5;
        border: 1px solid #A7F3D0;
        color: #065F46;
        font-size: 0.73rem;
        font-weight: 600;
        padding: 0.25rem 0.6rem;
        border-radius: 6px;
        margin-bottom: 0.95rem;
        width: 100%;
    }}

    .status-dot {{
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background-color: #10B981;
        box-shadow: 0 0 0 2px rgba(16, 185, 129, 0.25);
    }}

    /* Sidebar Section Divider / Header */
    .sidebar-section-header {{
        font-size: 0.68rem;
        font-weight: 700;
        color: {COLOR_TEXT_MUTED};
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-top: 0.85rem;
        margin-bottom: 0.45rem;
    }}

    /* Sidebar Radio Buttons Styling */
    [data-testid="stSidebar"] [data-testid="stRadio"] > div {{
        gap: 0.3rem !important;
    }}

    [data-testid="stSidebar"] [data-testid="stRadio"] label {{
        background-color: #FFFFFF !important;
        border: 1px solid {COLOR_BORDER} !important;
        border-radius: 8px !important;
        padding: 0.55rem 0.85rem !important;
        margin-bottom: 0.25rem !important;
        font-size: 0.84rem !important;
        font-weight: 600 !important;
        color: {COLOR_TEXT_BODY} !important;
        cursor: pointer !important;
        transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1) !important;
        display: flex !important;
        align-items: center !important;
    }}

    [data-testid="stSidebar"] [data-testid="stRadio"] label:hover {{
        background-color: {COLOR_CANVAS} !important;
        border-color: {COLOR_BORDER_STRONG} !important;
        color: {COLOR_TEXT_DARK} !important;
        transform: translateX(2px) !important;
    }}

    /* Active Radio Item */
    [data-testid="stSidebar"] [data-testid="stRadio"] label[data-checked="true"],
    [data-testid="stSidebar"] [data-testid="stRadio"] div[aria-checked="true"] {{
        background-color: {COLOR_PRIMARY_LIGHT} !important;
        border: 1.5px solid {COLOR_PRIMARY} !important;
        color: {COLOR_PRIMARY_DARK} !important;
        font-weight: 700 !important;
        box-shadow: 0 2px 6px rgba(194, 65, 12, 0.12) !important;
    }}

    /* =========================================================================
       4. TOP TITLE & ACTION BAR
       ========================================================================= */
    .page-title {{
        font-size: clamp(1.35rem, 2.2vw, 1.75rem);
        font-weight: 800;
        color: {COLOR_TEXT_DARK};
        letter-spacing: -0.025em;
        margin-bottom: 0.15rem;
        line-height: 1.2;
    }}

    .page-caption {{
        font-size: 0.84rem;
        color: {COLOR_TEXT_MUTED};
        margin-bottom: 0.85rem;
        line-height: 1.4;
    }}

    /* =========================================================================
       5. METRIC CARDS & GRID (RESPONSIVE)
       ========================================================================= */
    .metric-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
        gap: 0.75rem;
        margin-bottom: 0.85rem;
    }}

    .metric-card {{
        background-color: #FFFFFF;
        border: 1px solid {COLOR_BORDER};
        border-top: 3.5px solid {COLOR_PRIMARY};
        border-radius: 8px;
        padding: 0.85rem 1rem;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.03);
        transition: transform 0.2s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.2s ease;
    }}

    .metric-card:hover {{
        transform: translateY(-2px);
        box-shadow: 0 6px 14px rgba(0, 0, 0, 0.06);
    }}

    .metric-title {{
        font-size: 0.73rem;
        font-weight: 700;
        color: {COLOR_TEXT_MUTED};
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.35rem;
    }}

    .metric-value {{
        font-size: clamp(1.4rem, 2vw, 1.85rem);
        font-weight: 800;
        color: {COLOR_TEXT_DARK};
        letter-spacing: -0.025em;
        line-height: 1.1;
        margin-bottom: 0.25rem;
    }}

    .metric-sub {{
        font-size: 0.75rem;
        color: {COLOR_TEXT_MUTED};
        font-weight: 500;
        display: flex;
        align-items: center;
        gap: 0.3rem;
    }}

    /* =========================================================================
       6. EXECUTIVE CONTENT CARDS & BANNERS
       ========================================================================= */
    .exec-card {{
        background-color: #FFFFFF;
        border: 1px solid {COLOR_BORDER};
        border-radius: 10px;
        padding: 0.95rem 1.05rem;
        margin-bottom: 0.85rem;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.025);
    }}

    .exec-card-header {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.75rem;
        padding-bottom: 0.45rem;
        border-bottom: 1px solid {COLOR_BORDER};
        flex-wrap: wrap;
        gap: 0.5rem;
    }}

    .exec-card-title {{
        font-size: 0.92rem;
        font-weight: 700;
        color: {COLOR_TEXT_DARK};
        letter-spacing: -0.01em;
    }}

    .exec-card-badge {{
        background-color: {COLOR_PRIMARY_LIGHT};
        color: {COLOR_PRIMARY_DARK};
        font-size: 0.7rem;
        font-weight: 700;
        padding: 0.18rem 0.5rem;
        border-radius: 4px;
        border: 1px solid {COLOR_PRIMARY_BORDER};
        letter-spacing: 0.02em;
    }}

    .rust-banner {{
        background-color: {COLOR_PRIMARY_LIGHT};
        border: 1px solid {COLOR_PRIMARY_BORDER};
        border-left: 4px solid {COLOR_PRIMARY};
        border-radius: 8px;
        padding: 0.65rem 0.95rem;
        margin-bottom: 0.85rem;
        font-size: 0.83rem;
        color: {COLOR_TEXT_BODY};
        line-height: 1.45;
    }}

    /* =========================================================================
       7. COLLAPSIBLE SIDE-CHAT DRAWER STYLING
       ========================================================================= */
    .sidechat-container {{
        background-color: #FFFFFF;
        border: 1px solid {COLOR_BORDER};
        border-radius: 10px;
        padding: 0.9rem;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.04);
        display: flex;
        flex-direction: column;
        height: 100%;
    }}

    .sidechat-header {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding-bottom: 0.65rem;
        border-bottom: 1.5px solid {COLOR_BORDER};
        margin-bottom: 0.75rem;
    }}

    .sidechat-title {{
        font-size: 0.9rem;
        font-weight: 800;
        color: {COLOR_TEXT_DARK};
        display: flex;
        align-items: center;
        gap: 0.45rem;
    }}

    .sidechat-badge {{
        background-color: #ECFDF5;
        color: #065F46;
        border: 1px solid #A7F3D0;
        font-size: 0.68rem;
        font-weight: 700;
        padding: 0.15rem 0.45rem;
        border-radius: 4px;
    }}

    /* Chat message bubbles */
    .chat-bubble-user {{
        background-color: {COLOR_PRIMARY_LIGHT};
        border: 1px solid {COLOR_PRIMARY_BORDER};
        border-radius: 8px 8px 0px 8px;
        padding: 0.6rem 0.8rem;
        font-size: 0.82rem;
        color: {COLOR_PRIMARY_DARK};
        margin-bottom: 0.5rem;
        margin-left: 1.5rem;
        line-height: 1.4;
    }}

    .chat-bubble-bot {{
        background-color: #FFFFFF;
        border: 1px solid {COLOR_BORDER};
        border-left: 3px solid {COLOR_PRIMARY};
        border-radius: 0px 8px 8px 8px;
        padding: 0.65rem 0.85rem;
        font-size: 0.82rem;
        color: {COLOR_TEXT_BODY};
        margin-bottom: 0.65rem;
        margin-right: 0.75rem;
        line-height: 1.45;
        box-shadow: 0 1px 4px rgba(0, 0, 0, 0.02);
    }}

    .bot-section-title {{
        font-size: 0.72rem;
        font-weight: 700;
        color: {COLOR_PRIMARY_DARK};
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-top: 0.4rem;
        margin-bottom: 0.2rem;
    }}

    .bot-action-box {{
        background-color: #FFFBF7;
        border: 1px solid {COLOR_PRIMARY_BORDER};
        border-radius: 6px;
        padding: 0.45rem 0.65rem;
        margin-top: 0.45rem;
        font-size: 0.79rem;
        color: #9A3412;
    }}

    /* Modern Streamlit Button Overrides */
    div.stButton > button {{
        background-color: #FFFFFF !important;
        border: 1px solid {COLOR_BORDER} !important;
        color: {COLOR_TEXT_BODY} !important;
        border-radius: 6px !important;
        font-size: 0.8rem !important;
        font-weight: 600 !important;
        padding: 0.35rem 0.75rem !important;
        transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1) !important;
    }}

    div.stButton > button:hover {{
        background-color: {COLOR_CANVAS} !important;
        border-color: {COLOR_PRIMARY} !important;
        color: {COLOR_PRIMARY} !important;
        transform: translateY(-1px) !important;
    }}

    /* Primary Buttons */
    div.stButton > button[kind="primary"] {{
        background-color: {COLOR_PRIMARY} !important;
        border-color: {COLOR_PRIMARY} !important;
        color: #FFFFFF !important;
        box-shadow: 0 2px 6px rgba(194, 65, 12, 0.25) !important;
    }}

    div.stButton > button[kind="primary"]:hover {{
        background-color: {COLOR_PRIMARY_DARK} !important;
        border-color: {COLOR_PRIMARY_DARK} !important;
        color: #FFFFFF !important;
    }}
</style>
"""

# ------------------------------------------------------------------------------
# 3. UNIFIED PLOTLY LAYOUT HELPER
# ------------------------------------------------------------------------------
def apply_clean_layout(fig, title="", height=280):
    """
    Applies consistent executive styling to Plotly figures:
    - Pure white/transparent canvas
    - Slate typography and hairline gridlines
    - Zero outer margin waste
    - Fully responsive
    """
    fig.update_layout(
        title=dict(
            text=f"<b>{title}</b>" if title else "",
            font=dict(size=13, color=COLOR_TEXT_DARK, family="-apple-system, BlinkMacSystemFont, Segoe UI, Roboto"),
            x=0.01,
            y=0.96
        ) if title else None,
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=15, r=15, t=35 if title else 15, b=15),
        font=dict(family="-apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif", size=11, color=COLOR_TEXT_BODY),
        xaxis=dict(
            showgrid=False,
            zeroline=False,
            tickfont=dict(size=10, color=COLOR_TEXT_MUTED),
            linecolor=COLOR_BORDER,
            tickcolor=COLOR_BORDER
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="#F1F5F9",
            zeroline=False,
            tickfont=dict(size=10, color=COLOR_TEXT_MUTED),
            linecolor=COLOR_BORDER
        ),
        autosize=True
    )
    return fig

