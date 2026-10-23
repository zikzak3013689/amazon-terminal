"""
Theme and custom CSS styling for the Amazon India Product Research Terminal.
Delivers a sleek, modern financial research terminal aesthetic.
"""

import streamlit as st

def apply_terminal_theme():
    """Injects financial terminal CSS styles."""
    st.markdown("""
    <style>
    /* Global Terminal Typography and Color Accents */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    code, pre, .mono-font {
        font-family: 'JetBrains Mono', monospace;
    }

    /* Terminal Header Bar */
    .terminal-header {
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 18px 24px;
        margin-bottom: 24px;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.25);
    }

    .terminal-title {
        color: #F8FAFC;
        font-size: 1.6rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 12px;
    }

    .terminal-subtitle {
        color: #94A3B8;
        font-size: 0.88rem;
        margin-top: 4px;
        font-weight: 500;
    }

    /* Metric Cards */
    .metric-card {
        background: #1E293B;
        border: 1px solid #334155;
        border-radius: 8px;
        padding: 16px 20px;
        transition: transform 0.15s ease, border-color 0.15s ease;
    }

    .metric-card:hover {
        border-color: #38BDF8;
        transform: translateY(-2px);
    }

    .metric-label {
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #94A3B8;
        margin-bottom: 6px;
    }

    .metric-value {
        font-size: 1.75rem;
        font-weight: 700;
        color: #F8FAFC;
        font-family: 'JetBrains Mono', monospace;
    }

    .metric-sub {
        font-size: 0.8rem;
        color: #64748B;
        margin-top: 4px;
    }

    /* Provenance Data Badges */
    .badge-observed {
        background-color: rgba(16, 185, 129, 0.15);
        color: #10B981;
        border: 1px solid rgba(16, 185, 129, 0.3);
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.72rem;
        font-weight: 600;
        text-transform: uppercase;
    }

    .badge-estimated {
        background-color: rgba(56, 189, 248, 0.15);
        color: #38BDF8;
        border: 1px solid rgba(56, 189, 248, 0.3);
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.72rem;
        font-weight: 600;
        text-transform: uppercase;
    }

    .badge-calculated {
        background-color: rgba(168, 85, 247, 0.15);
        color: #C084FC;
        border: 1px solid rgba(168, 85, 247, 0.3);
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.72rem;
        font-weight: 600;
        text-transform: uppercase;
    }

    .badge-assumed {
        background-color: rgba(245, 158, 11, 0.15);
        color: #FBBF24;
        border: 1px solid rgba(245, 158, 11, 0.3);
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.72rem;
        font-weight: 600;
        text-transform: uppercase;
    }

    /* Mode Banners */
    .demo-banner {
        background: rgba(239, 68, 68, 0.12);
        border: 1px solid rgba(239, 68, 68, 0.35);
        border-radius: 6px;
        padding: 10px 16px;
        color: #FCA5A5;
        font-size: 0.85rem;
        font-weight: 600;
        margin-bottom: 18px;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    .real-banner {
        background: rgba(16, 185, 129, 0.12);
        border: 1px solid rgba(16, 185, 129, 0.35);
        border-radius: 6px;
        padding: 10px 16px;
        color: #6EE7B7;
        font-size: 0.85rem;
        font-weight: 600;
        margin-bottom: 18px;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    /* Scenario Comparison Card */
    .scenario-card {
        background: #1E293B;
        border: 1px solid #334155;
        border-radius: 8px;
        padding: 16px;
        text-align: center;
    }

    .scenario-conservative {
        border-top: 4px solid #F59E0B;
    }

    .scenario-base {
        border-top: 4px solid #38BDF8;
        background: #172554;
    }

    .scenario-optimistic {
        border-top: 4px solid #10B981;
    }

    /* Checklist Status Badges */
    .status-pass {
        color: #10B981;
        font-weight: 700;
    }

    .status-investigate {
        color: #F59E0B;
        font-weight: 700;
    }

    .status-fail {
        color: #EF4444;
        font-weight: 700;
    }
    </style>
    """, unsafe_allow_html=True)
