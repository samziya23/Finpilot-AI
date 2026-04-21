# app.py
# FinPilot AI — Agentic Financial Assistant
# ─────────────────────────────────────────
# UI redesign: premium SaaS dark theme
# Backend logic: UNCHANGED
# Run: streamlit run app.py

import sys
import os

project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from utils.helpers import load_and_validate_csv, format_currency
from agent import run_agent
from tools.analysis_tool import expense_analysis_tool
from tools.prediction_tool import prediction_tool
from tools.suggestion_tool import savings_suggestion_tool
from tools.anomaly_tool import anomaly_detection_tool

# ══════════════════════════════════════════════════════════════════
# PAGE CONFIG
# ══════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="FinPilot — AI Financial Copilot",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════════════════
# DESIGN SYSTEM CSS
# Palette: Deep Navy · Teal · Emerald · Warm Gold
# ══════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── TOKENS ─────────────────────────────────────────────────── */
:root {
  --navy-950:  #050912;
  --navy-900:  #080F1E;
  --navy-800:  #0C1528;
  --navy-700:  #101C34;
  --navy-600:  #162240;
  --navy-500:  #1E2E52;

  --teal-500:  #0F9D8C;
  --teal-400:  #13B5A2;
  --teal-300:  #2DD4BF;
  --teal-glow: rgba(15,157,140,0.18);
  --teal-edge: rgba(15,157,140,0.30);

  --emerald:   #10B981;
  --emerald-m: rgba(16,185,129,0.12);
  --emerald-b: rgba(16,185,129,0.25);

  --gold:      #D4A853;
  --gold-m:    rgba(212,168,83,0.12);
  --gold-b:    rgba(212,168,83,0.28);

  --red:       #F43F5E;
  --red-m:     rgba(244,63,94,0.10);
  --red-b:     rgba(244,63,94,0.22);

  --amber:     #F59E0B;
  --amber-m:   rgba(245,158,11,0.10);
  --amber-b:   rgba(245,158,11,0.22);

  --text-100:  #F0F6FF;
  --text-200:  #C8D6F0;
  --text-400:  #7A8EAD;
  --text-600:  #3A4A65;

  --border:    rgba(255,255,255,0.06);
  --border-md: rgba(255,255,255,0.10);

  --radius-sm: 8px;
  --radius:    14px;
  --radius-lg: 20px;
}

/* ── BASE ───────────────────────────────────────────────────── */
html, body, .stApp {
  background: var(--navy-950) !important;
  font-family: 'Plus Jakarta Sans', sans-serif !important;
  color: var(--text-100) !important;
}
#MainMenu, footer, header { visibility: hidden !important; }
.block-container {
  padding: 0 2.5rem 5rem !important;
  max-width: 1380px !important;
}

/* ── SIDEBAR ────────────────────────────────────────────────── */
[data-testid="stSidebar"] {
  background: var(--navy-800) !important;
  border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] > div:first-child { padding-top: 0 !important; }

/* ── FILE UPLOADER ──────────────────────────────────────────── */
[data-testid="stFileUploader"] > div {
  background: var(--navy-700) !important;
  border: 1.5px dashed var(--teal-edge) !important;
  border-radius: var(--radius) !important;
  transition: border-color 0.2s !important;
}
[data-testid="stFileUploader"] > div:hover {
  border-color: var(--teal-400) !important;
}
[data-testid="stFileUploaderDropzoneInstructions"] {
  color: var(--text-400) !important;
  font-size: 0.82rem !important;
}

/* ── BUTTONS ────────────────────────────────────────────────── */
.stButton > button {
  font-family: 'Plus Jakarta Sans', sans-serif !important;
  font-weight: 600 !important;
  font-size: 0.875rem !important;
  border-radius: 10px !important;
  padding: 0.55rem 1.4rem !important;
  transition: all 0.2s ease !important;
  border: 1px solid var(--teal-edge) !important;
  background: var(--teal-glow) !important;
  color: var(--teal-300) !important;
  letter-spacing: 0.01em !important;
}
.stButton > button:hover {
  background: rgba(15,157,140,0.28) !important;
  border-color: var(--teal-400) !important;
  box-shadow: 0 0 18px var(--teal-glow) !important;
  transform: translateY(-1px) !important;
}
.stButton > button[kind="primary"] {
  background: linear-gradient(135deg, #0F9D8C 0%, #0C7A6D 100%) !important;
  border: none !important;
  color: #fff !important;
  box-shadow: 0 4px 20px rgba(15,157,140,0.38) !important;
}
.stButton > button[kind="primary"]:hover {
  box-shadow: 0 6px 28px rgba(15,157,140,0.52) !important;
  transform: translateY(-2px) !important;
}

/* ── TEXT INPUT ─────────────────────────────────────────────── */
.stTextInput > div > div > input {
  background: var(--navy-700) !important;
  border: 1px solid var(--border-md) !important;
  border-radius: var(--radius-sm) !important;
  color: var(--text-100) !important;
  font-family: 'Plus Jakarta Sans', sans-serif !important;
  font-size: 0.9rem !important;
  padding: 0.7rem 1rem !important;
  transition: border-color 0.2s, box-shadow 0.2s !important;
}
.stTextInput > div > div > input:focus {
  border-color: var(--teal-400) !important;
  box-shadow: 0 0 0 3px var(--teal-glow) !important;
  outline: none !important;
}
.stTextInput > div > div > input::placeholder { color: var(--text-600) !important; }

/* ── EXPANDERS ──────────────────────────────────────────────── */
[data-testid="stExpander"] {
  background: var(--navy-800) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius-sm) !important;
}
[data-testid="stExpander"] summary {
  color: var(--text-400) !important;
  font-size: 0.82rem !important;
  font-weight: 500 !important;
}

/* ── INFO / ALERT BOX ───────────────────────────────────────── */
.stAlert {
  background: var(--navy-700) !important;
  border: 1px solid var(--teal-edge) !important;
  border-radius: var(--radius-sm) !important;
  color: var(--text-200) !important;
}

/* ── PLOTLY CHART WRAPPER ───────────────────────────────────── */
.js-plotly-plot { border-radius: var(--radius) !important; }

/* ── SCROLLBAR ──────────────────────────────────────────────── */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--teal-edge); border-radius: 10px; }

/* ── ANIMATIONS ─────────────────────────────────────────────── */
@keyframes fadeUp {
  from { opacity: 0; transform: translateY(16px); }
  to   { opacity: 1; transform: translateY(0); }
}
@keyframes shimmer {
  0%   { background-position: -200% center; }
  100% { background-position:  200% center; }
}
@keyframes pulse-dot {
  0%, 100% { opacity: 1; }
  50%       { opacity: 0.4; }
}

/* ── UTILITY CLASSES ────────────────────────────────────────── */
.fade-up { animation: fadeUp 0.55s ease both; }

/* Badge */
.fp-badge {
  display: inline-flex; align-items: center; gap: 5px;
  padding: 0.22rem 0.7rem; border-radius: 9999px;
  font-size: 0.68rem; font-weight: 700; letter-spacing: 0.06em; text-transform: uppercase;
}
.fp-badge-teal   { background: var(--teal-glow);  color: var(--teal-300);  border: 1px solid var(--teal-edge); }
.fp-badge-green  { background: var(--emerald-m);  color: var(--emerald);   border: 1px solid var(--emerald-b); }
.fp-badge-red    { background: var(--red-m);       color: var(--red);       border: 1px solid var(--red-b); }
.fp-badge-amber  { background: var(--amber-m);     color: var(--amber);     border: 1px solid var(--amber-b); }
.fp-badge-gold   { background: var(--gold-m);      color: var(--gold);      border: 1px solid var(--gold-b); }
.fp-badge-grey   { background: rgba(122,142,173,0.08); color: var(--text-400); border: 1px solid rgba(122,142,173,0.15); }

/* Section heading */
.fp-section-heading {
  font-size: 0.7rem; font-weight: 700; letter-spacing: 0.12em;
  text-transform: uppercase; color: var(--text-600);
  padding-bottom: 0.9rem; margin-bottom: 0.1rem;
  border-bottom: 1px solid var(--border);
  display: flex; align-items: center; gap: 0.5rem;
}
.fp-section-dot {
  width: 6px; height: 6px; border-radius: 50%;
  display: inline-block;
}

/* Metric card */
.fp-metric {
  background: var(--navy-800);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 1.4rem 1.6rem;
  position: relative; overflow: hidden;
  transition: border-color 0.25s, box-shadow 0.25s, transform 0.2s;
}
.fp-metric::after {
  content: '';
  position: absolute; top: 0; left: 0; right: 0; height: 2px;
  background: linear-gradient(90deg, var(--teal-500), var(--gold));
  opacity: 0; transition: opacity 0.3s;
}
.fp-metric:hover {
  border-color: var(--teal-edge); box-shadow: 0 4px 28px var(--teal-glow);
  transform: translateY(-2px);
}
.fp-metric:hover::after { opacity: 1; }
.fp-metric-label {
  font-size: 0.62rem; font-weight: 700; letter-spacing: 0.12em;
  text-transform: uppercase; color: var(--text-600); margin-bottom: 0.6rem;
}
.fp-metric-val {
  font-family: 'JetBrains Mono', monospace;
  font-size: 1.85rem; font-weight: 500;
  color: var(--text-100); line-height: 1; letter-spacing: -0.02em;
}
.fp-metric-val-sm {
  font-size: 1.3rem; font-weight: 700;
  color: var(--text-100); line-height: 1.15;
}
.fp-metric-sub { margin-top: 0.55rem; }

/* Suggestion card */
.fp-suggest {
  background: var(--navy-800);
  border: 1px solid var(--border);
  border-left: 3px solid var(--teal-500);
  border-radius: var(--radius);
  padding: 1.2rem 1.5rem; margin-bottom: 0.8rem;
  transition: border-color 0.2s, box-shadow 0.2s;
}
.fp-suggest:hover {
  border-color: var(--teal-edge);
  box-shadow: 0 2px 20px var(--teal-glow);
}

/* Anomaly card */
.fp-anomaly-warn {
  background: rgba(244,63,94,0.04);
  border: 1px solid var(--red-b); border-radius: var(--radius);
  padding: 1.5rem; margin-bottom: 0.75rem;
}
.fp-anomaly-ok {
  background: rgba(16,185,129,0.04);
  border: 1px solid var(--emerald-b); border-radius: var(--radius);
  padding: 1.4rem;
}
.fp-anomaly-row {
  display: flex; justify-content: space-between; align-items: center;
  padding: 0.6rem 0; border-bottom: 1px solid rgba(255,255,255,0.04);
}
.fp-anomaly-row:last-child { border-bottom: none; }

/* Pipeline blocks */
.fp-pipeline-wrap {
  background: rgba(15,157,140,0.03);
  border: 1px solid var(--teal-edge);
  border-radius: var(--radius); padding: 1.6rem 1.8rem; margin-bottom: 1.4rem;
}
.fp-pipeline-step {
  background: var(--navy-800); border: 1px solid var(--border);
  border-radius: var(--radius-sm); padding: 0.9rem 1.15rem; margin-bottom: 0.5rem;
}
.fp-pipe-label {
  font-size: 0.6rem; font-weight: 700; letter-spacing: 0.1em;
  text-transform: uppercase; color: var(--text-600); margin-bottom: 0.35rem;
}
.fp-pipe-val {
  font-size: 0.88rem; font-weight: 500; color: var(--text-100);
}
.fp-reasoning-row {
  display: flex; align-items: flex-start; gap: 0.7rem;
  padding: 0.55rem 0; border-bottom: 1px solid rgba(255,255,255,0.03);
  font-size: 0.83rem; color: var(--text-400);
}
.fp-reasoning-row:last-child { border-bottom: none; }
.fp-step-pill {
  font-size: 0.62rem; font-weight: 700;
  color: var(--teal-300); background: var(--teal-glow);
  border: 1px solid var(--teal-edge); border-radius: 4px;
  padding: 2px 7px; white-space: nowrap; margin-top: 1px;
  font-family: 'JetBrains Mono', monospace;
}

/* Query bubble */
.fp-query-bubble {
  background: rgba(15,157,140,0.06);
  border: 1px solid var(--teal-edge); border-radius: var(--radius-sm);
  padding: 0.8rem 1.1rem; margin-bottom: 0.6rem;
}

/* How it works step */
.fp-how-step {
  background: var(--navy-800); border: 1px solid var(--border);
  border-radius: var(--radius); padding: 1.4rem 1.2rem; text-align: center;
  transition: border-color 0.2s, box-shadow 0.2s, transform 0.2s;
}
.fp-how-step:hover {
  border-color: var(--teal-edge);
  box-shadow: 0 4px 24px var(--teal-glow);
  transform: translateY(-3px);
}
.fp-how-num {
  width: 36px; height: 36px; border-radius: 10px;
  background: linear-gradient(135deg, #0F9D8C, #0C7A6D);
  font-size: 0.9rem; font-weight: 800; color: #fff;
  display: flex; align-items: center; justify-content: center;
  margin: 0 auto 0.8rem;
}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# CHART HELPERS  (unchanged logic, updated visual theme)
# ══════════════════════════════════════════════════════════════════
_THEME = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Plus Jakarta Sans", color="#7A8EAD", size=12),
    margin=dict(l=8, r=8, t=40, b=16),
)
_COLORS = ["#0F9D8C", "#D4A853", "#10B981", "#7C3AED", "#F43F5E", "#06B6D4", "#F97316"]


def chart_categories(cat_totals: dict, cat_pct: dict = None) -> go.Figure:
    cats, vals = list(cat_totals.keys()), list(cat_totals.values())
    fig = go.Figure(go.Bar(
        x=cats, y=vals,
        marker_color=_COLORS[:len(cats)],
        marker_line_width=0,
        text=[f"₹{v:,.0f}" for v in vals],
        textposition="outside",
        textfont=dict(color="#C8D6F0", size=11, family="JetBrains Mono"),
        hovertemplate="<b>%{x}</b><br>₹%{y:,.0f}<extra></extra>",
    ))
    fig.update_layout(
        **_THEME,
        title=dict(text="<b>Spending by Category</b>", font=dict(color="#F0F6FF", size=14, family="Plus Jakarta Sans")),
        xaxis=dict(gridcolor="rgba(255,255,255,0.04)", tickfont=dict(color="#7A8EAD"), showline=False),
        yaxis=dict(gridcolor="rgba(255,255,255,0.04)", tickprefix="₹", tickfont=dict(color="#7A8EAD"), showline=False),
        height=320, bargap=0.35,
    )
    return fig


def chart_monthly(monthly_totals: dict, mom_change: dict = None) -> go.Figure:
    months, vals = list(monthly_totals.keys()), list(monthly_totals.values())
    hover = []
    for m, v in zip(months, vals):
        mom = mom_change.get(m) if mom_change else None
        if mom is not None:
            arrow = "▲" if mom > 0 else "▼"
            c = "F43F5E" if mom > 0 else "10B981"
            hover.append(f"<b>{m}</b><br>₹{v:,.0f}<br><span style='color:#{c}'>{arrow} {abs(mom):.1f}% MoM</span>")
        else:
            hover.append(f"<b>{m}</b><br>₹{v:,.0f}<br>Baseline")
    fig = go.Figure(go.Scatter(
        x=months, y=vals, mode="lines+markers",
        line=dict(color="#0F9D8C", width=2.5, shape="spline"),
        marker=dict(size=8, color="#0F9D8C", line=dict(color="#2DD4BF", width=1.5)),
        fill="tozeroy", fillcolor="rgba(15,157,140,0.07)",
        hovertemplate="%{customdata}<extra></extra>", customdata=hover,
    ))
    fig.update_layout(
        **_THEME,
        title=dict(text="<b>Monthly Spending Trend</b>", font=dict(color="#F0F6FF", size=14, family="Plus Jakarta Sans")),
        xaxis=dict(gridcolor="rgba(255,255,255,0.04)", tickfont=dict(color="#7A8EAD"), showline=False),
        yaxis=dict(gridcolor="rgba(255,255,255,0.04)", tickprefix="₹", tickfont=dict(color="#7A8EAD"), showline=False),
        height=320,
    )
    return fig


def chart_prediction(monthly_data: list, predicted_amount: float, next_label: str) -> go.Figure:
    months = [d["month"] for d in monthly_data]
    actuals = [d["amount"] for d in monthly_data]
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=months, y=actuals, mode="lines+markers", name="Actual",
        line=dict(color="#0F9D8C", width=2.5, shape="spline"),
        marker=dict(size=7, color="#0F9D8C"),
        hovertemplate="<b>%{x}</b><br>₹%{y:,.0f}<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=[next_label], y=[predicted_amount], mode="markers+text", name="Forecast",
        marker=dict(size=14, color="#D4A853", symbol="diamond", line=dict(color="#F0C878", width=1.5)),
        text=[f"<b>₹{predicted_amount:,.0f}</b>"],
        textposition="top center", textfont=dict(color="#D4A853", size=12, family="JetBrains Mono"),
        hovertemplate=f"<b>Forecast: {next_label}</b><br>₹{predicted_amount:,.0f}<extra></extra>",
    ))
    if months:
        fig.add_trace(go.Scatter(
            x=[months[-1], next_label], y=[actuals[-1], predicted_amount],
            mode="lines", line=dict(color="#D4A853", width=1.8, dash="dash"),
            showlegend=False, hoverinfo="skip",
        ))
    fig.update_layout(
        **_THEME,
        title=dict(text="<b>Expense Forecast</b>", font=dict(color="#F0F6FF", size=14, family="Plus Jakarta Sans")),
        xaxis=dict(gridcolor="rgba(255,255,255,0.04)", tickfont=dict(color="#7A8EAD"), showline=False),
        yaxis=dict(gridcolor="rgba(255,255,255,0.04)", tickprefix="₹", tickfont=dict(color="#7A8EAD"), showline=False),
        height=320,
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#7A8EAD")),
    )
    return fig


def chart_anomaly(monthly_data: list, anomalies: list) -> go.Figure:
    anomaly_months = {a["month"] for a in anomalies}
    months = [d["month"] for d in monthly_data]
    amounts = [d["amount"] for d in monthly_data]
    colors = ["#F43F5E" if m in anomaly_months else "#0F9D8C" for m in months]
    fig = go.Figure(go.Bar(
        x=months, y=amounts, marker_color=colors, marker_line_width=0,
        text=[f"₹{v:,.0f}" for v in amounts],
        textposition="outside",
        textfont=dict(color="#C8D6F0", size=10, family="JetBrains Mono"),
        hovertemplate="<b>%{x}</b><br>₹%{y:,.0f}<br>%{customdata}<extra></extra>",
        customdata=["⚠ Anomaly" if m in anomaly_months else "Normal" for m in months],
    ))
    fig.update_layout(
        **_THEME,
        title=dict(text="<b>Monthly Spending — Anomalies Highlighted</b>", font=dict(color="#F0F6FF", size=14, family="Plus Jakarta Sans")),
        xaxis=dict(gridcolor="rgba(255,255,255,0.04)", tickfont=dict(color="#7A8EAD"), showline=False),
        yaxis=dict(gridcolor="rgba(255,255,255,0.04)", tickprefix="₹", tickfont=dict(color="#7A8EAD"), showline=False),
        height=300, bargap=0.35,
    )
    return fig


# ══════════════════════════════════════════════════════════════════
# BADGE HELPERS
# ══════════════════════════════════════════════════════════════════
def badge_mom(pct):
    if pct is None:
        return ''
    if pct > 0:
        return f'<span class="fp-badge fp-badge-red">▲ {abs(pct):.1f}% vs last month</span>'
    elif pct < 0:
        return f'<span class="fp-badge fp-badge-green">▼ {abs(pct):.1f}% vs last month</span>'
    return '<span class="fp-badge fp-badge-grey">→ Stable</span>'

def badge_conf(label, score):
    cls_map = {"High": "fp-badge-green", "Medium": "fp-badge-amber", "Low": "fp-badge-red"}
    cls = cls_map.get(label, "fp-badge-grey")
    return f'<span class="fp-badge {cls}">◉ {label} Confidence &nbsp;{score:.0f}%</span>'

def badge_sev(sev):
    if sev == "high":
        return '<span class="fp-badge fp-badge-red">HIGH</span>'
    return '<span class="fp-badge fp-badge-amber">MEDIUM</span>'


# ══════════════════════════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════════════════════════
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "df" not in st.session_state:
    st.session_state.df = None
if "input_counter" not in st.session_state:
    st.session_state.input_counter = 0


# ══════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════
with st.sidebar:

    # — Brand —
    st.markdown("""
    <div style="padding: 1.8rem 0 1.6rem; border-bottom: 1px solid rgba(255,255,255,0.06);">
      <div style="display:flex; align-items:center; gap:0.65rem; margin-bottom:0.4rem;">
        <div style="width:36px; height:36px; border-radius:10px;
          background:linear-gradient(135deg,#0F9D8C,#D4A853);
          display:flex; align-items:center; justify-content:center;
          font-size:1.1rem; flex-shrink:0; box-shadow:0 4px 12px rgba(15,157,140,0.4);">✈️</div>
        <span style="font-size:1.35rem; font-weight:800; letter-spacing:-0.025em;
          color:#F0F6FF; font-family:'Plus Jakarta Sans',sans-serif;">FinPilot</span>
      </div>
      <p style="color:#3A4A65; font-size:0.77rem; margin:0; padding-left:0.15rem;
        font-family:'Plus Jakarta Sans',sans-serif; letter-spacing:0.02em;">
        AI-Powered Financial Copilot
      </p>
    </div>
    """, unsafe_allow_html=True)

    # — Upload —
    st.markdown("""
    <div style="padding: 1.2rem 0 0.5rem;">
      <div style="font-size:0.62rem; font-weight:700; letter-spacing:0.12em;
        text-transform:uppercase; color:#3A4A65; margin-bottom:0.65rem;">
        📂 &nbsp; Data Source
      </div>
    </div>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Upload CSV",
        type=["csv"],
        label_visibility="collapsed",
        help="CSV with columns: date, category, amount"
    )
    if uploaded_file:
        df_up, err = load_and_validate_csv(uploaded_file)
        if err:
            st.error(f"⚠ {err}")
        else:
            st.session_state.df = df_up
            st.markdown(f"""
            <div style="margin-top:0.5rem; padding:0.55rem 0.9rem;
              background:rgba(16,185,129,0.08); border:1px solid rgba(16,185,129,0.22);
              border-radius:8px; font-size:0.8rem; color:#10B981;">
              ✓ &nbsp; {len(df_up):,} records loaded
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div style='height:0.6rem'></div>", unsafe_allow_html=True)
    if st.button("⚡  Load Sample Data", use_container_width=True, type="primary"):
        try:
            df_s = pd.read_csv("sample_data.csv")
            df_s.columns = [c.strip().lower() for c in df_s.columns]
            df_s["date"] = pd.to_datetime(df_s["date"])
            df_s["amount"] = pd.to_numeric(df_s["amount"])
            st.session_state.df = df_s
            st.success("Sample data loaded successfully.")
        except Exception as e:
            st.error(f"Could not load sample data: {e}")

    # — Agent tools list —
    st.markdown("""
    <div style="margin-top:2rem; padding-top:1.4rem; border-top:1px solid rgba(255,255,255,0.06);">
      <div style="font-size:0.62rem; font-weight:700; letter-spacing:0.12em;
        text-transform:uppercase; color:#3A4A65; margin-bottom:0.85rem;">
        🤖 &nbsp; Agent Tools
      </div>
      <div style="display:flex; flex-direction:column; gap:0.45rem;">
        <div style="display:flex;align-items:center;gap:0.6rem;font-size:0.79rem;color:#7A8EAD;">
          <span style="width:7px;height:7px;background:#0F9D8C;border-radius:50%;box-shadow:0 0 6px #0F9D8C;flex-shrink:0;"></span>
          expense_analysis
        </div>
        <div style="display:flex;align-items:center;gap:0.6rem;font-size:0.79rem;color:#7A8EAD;">
          <span style="width:7px;height:7px;background:#D4A853;border-radius:50%;box-shadow:0 0 6px #D4A853;flex-shrink:0;"></span>
          spending_prediction
        </div>
        <div style="display:flex;align-items:center;gap:0.6rem;font-size:0.79rem;color:#7A8EAD;">
          <span style="width:7px;height:7px;background:#10B981;border-radius:50%;box-shadow:0 0 6px #10B981;flex-shrink:0;"></span>
          savings_suggestions
        </div>
        <div style="display:flex;align-items:center;gap:0.6rem;font-size:0.79rem;color:#7A8EAD;">
          <span style="width:7px;height:7px;background:#F43F5E;border-radius:50%;box-shadow:0 0 6px #F43F5E;flex-shrink:0;"></span>
          anomaly_detection
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # — CSV format hint —
    st.markdown("""
    <div style="margin-top:1.8rem; padding-top:1.2rem; border-top:1px solid rgba(255,255,255,0.06);">
      <div style="font-size:0.62rem; font-weight:700; letter-spacing:0.12em;
        text-transform:uppercase; color:#3A4A65; margin-bottom:0.55rem;">
        📋 &nbsp; CSV Format
      </div>
      <div style="background:rgba(15,157,140,0.06); border:1px solid rgba(15,157,140,0.15);
        border-radius:7px; padding:0.65rem 0.85rem;
        font-family:'JetBrains Mono',monospace; font-size:0.72rem; color:#2DD4BF; line-height:1.9;">
        date, category, amount<br>
        2024-01-03, Food, 1200<br>
        2024-01-07, Transport, 450
      </div>
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════
# HERO SECTION  (always visible)
# ══════════════════════════════════════════════════════════════════
st.markdown("""
<div class="fade-up" style="
  padding: 3.5rem 0 2.8rem;
  border-bottom: 1px solid rgba(255,255,255,0.05);
  margin-bottom: 0.5rem;
">

  <!-- Live badge -->
  <div style="text-align:center; margin-bottom:1.4rem;">
    <span style="display:inline-flex; align-items:center; gap:7px;
      background:rgba(15,157,140,0.1); border:1px solid rgba(15,157,140,0.25);
      border-radius:9999px; padding:0.32rem 1rem;
      font-size:0.7rem; font-weight:700; color:#2DD4BF;
      letter-spacing:0.08em; text-transform:uppercase;">
      <span style="width:6px;height:6px;border-radius:50%;background:#2DD4BF;
        box-shadow:0 0 8px #2DD4BF; animation: pulse-dot 2s infinite;
        display:inline-block;"></span>
      Powered by Agentic AI &nbsp;·&nbsp; Real-Time Analytics
    </span>
  </div>

  <!-- Main title -->
  <h1 style="
    text-align:center; margin:0 0 0.6rem;
    font-size:3.6rem; font-weight:800; letter-spacing:-0.04em; line-height:1.05;
    background: linear-gradient(135deg, #2DD4BF 0%, #D4A853 55%, #2DD4BF 100%);
    background-size: 200% auto;
    -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text;
    animation: shimmer 5s linear infinite;
    font-family:'Plus Jakarta Sans',sans-serif;
  ">Welcome to FinPilot</h1>

  <!-- Subtitle -->
  <p style="text-align:center; margin:0 0 0.4rem;
    font-size:1.15rem; font-weight:500; color:#7A8EAD;
    font-family:'Plus Jakarta Sans',sans-serif;">
    Your AI Financial Copilot
  </p>

  <!-- Tagline -->
  <p style="text-align:center; margin:0 0 2rem;
    font-size:0.9rem; color:#3A4A65;
    font-family:'Plus Jakarta Sans',sans-serif; letter-spacing:0.03em;">
    Analyze &nbsp;•&nbsp; Predict &nbsp;•&nbsp; Optimize your spending in seconds
  </p>

  <!-- Feature pills -->
  <div style="display:flex; justify-content:center; flex-wrap:wrap; gap:0.55rem;">
    <span style="background:rgba(15,157,140,0.08);border:1px solid rgba(15,157,140,0.2);
      border-radius:9999px;padding:0.28rem 0.9rem;font-size:0.78rem;color:#2DD4BF;">
      📊 Expense Analysis</span>
    <span style="background:rgba(212,168,83,0.08);border:1px solid rgba(212,168,83,0.2);
      border-radius:9999px;padding:0.28rem 0.9rem;font-size:0.78rem;color:#D4A853;">
      📈 Smart Forecast</span>
    <span style="background:rgba(16,185,129,0.08);border:1px solid rgba(16,185,129,0.2);
      border-radius:9999px;padding:0.28rem 0.9rem;font-size:0.78rem;color:#10B981;">
      💰 Savings Insights</span>
    <span style="background:rgba(244,63,94,0.08);border:1px solid rgba(244,63,94,0.2);
      border-radius:9999px;padding:0.28rem 0.9rem;font-size:0.78rem;color:#F43F5E;">
      ⚠️ Anomaly Detection</span>
    <span style="background:rgba(15,157,140,0.08);border:1px solid rgba(15,157,140,0.2);
      border-radius:9999px;padding:0.28rem 0.9rem;font-size:0.78rem;color:#2DD4BF;">
      🤖 AI Agent Chat</span>
  </div>

</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════
# NO DATA STATE
# ══════════════════════════════════════════════════════════════════
if st.session_state.df is None:

    # — How It Works —
    st.markdown("""
    <div style="padding: 2.5rem 0 0.5rem;">
      <div class="fp-section-heading">
        <span class="fp-section-dot" style="background:#0F9D8C; box-shadow:0 0 8px #0F9D8C;"></span>
        How It Works
      </div>
    </div>
    """, unsafe_allow_html=True)

    h1, h2, h3, h4 = st.columns(4)
    steps = [
        ("01", "📂", "Upload Your Data",
         "Upload a CSV with date, category and amount columns — or load the built-in sample."),
        ("02", "💬", "Ask a Question",
         "Type any financial question: overspending, forecast, savings, anomalies."),
        ("03", "🤖", "AI Selects Tools",
         "The agent detects your intent and automatically runs the right analysis tools."),
        ("04", "✨", "Get Insights",
         "Receive data-driven, quantified financial insights specific to your spending."),
    ]
    for col, (num, icon, title, desc) in zip([h1, h2, h3, h4], steps):
        with col:
            st.markdown(f"""
            <div class="fp-how-step">
              <div class="fp-how-num">{num}</div>
              <div style="font-size:1.6rem; margin-bottom:0.5rem;">{icon}</div>
              <div style="font-size:0.9rem; font-weight:700; color:#F0F6FF;
                margin-bottom:0.4rem;">{title}</div>
              <div style="font-size:0.78rem; color:#7A8EAD; line-height:1.6;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # CTA box
    _, ctr, _ = st.columns([1, 2, 1])
    with ctr:
        st.markdown("""
        <div style="background:rgba(15,157,140,0.05); border:1px solid rgba(15,157,140,0.18);
          border-radius:14px; padding:1.4rem 1.8rem; text-align:center; margin-top:0.5rem;">
          <div style="font-size:1rem; font-weight:700; color:#F0F6FF; margin-bottom:0.4rem;">
            Ready to start?
          </div>
          <div style="font-size:0.85rem; color:#7A8EAD; line-height:1.6;">
            Upload your expense CSV or click
            <strong style="color:#2DD4BF;">⚡ Load Sample Data</strong>
            in the sidebar to explore a live demo.
          </div>
        </div>
        """, unsafe_allow_html=True)
    st.stop()


# ══════════════════════════════════════════════════════════════════
# DATA LOADED — compute all tools
# ══════════════════════════════════════════════════════════════════
df          = st.session_state.df
analysis    = expense_analysis_tool(df)
pred        = prediction_tool(df)
suggestions = savings_suggestion_tool(df)
anom        = anomaly_detection_tool(df)


# ══════════════════════════════════════════════════════════════════
# DASHBOARD SECTION
# ══════════════════════════════════════════════════════════════════
st.markdown("""
<div style="padding: 2rem 0 0.2rem;">
  <div style="display:flex; align-items:baseline; gap:0.75rem; margin-bottom:0.25rem;">
    <h2 style="font-size:1.9rem; font-weight:800; color:#F0F6FF;
      letter-spacing:-0.035em; margin:0; font-family:'Plus Jakarta Sans',sans-serif;">
      Dashboard
    </h2>
    <span class="fp-badge fp-badge-teal" style="animation: pulse-dot 2s infinite;">
      ● LIVE
    </span>
  </div>
  <p style="color:#3A4A65; font-size:0.85rem; margin:0 0 1.6rem;">
    Real-time intelligence from your uploaded expense data.
  </p>
</div>
""", unsafe_allow_html=True)

# ── 4 Metric Cards ──────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(f"""
    <div class="fp-metric">
      <div class="fp-metric-label">Total Spend</div>
      <div class="fp-metric-val">{format_currency(analysis['total_spending'])}</div>
      <div class="fp-metric-sub">{badge_mom(analysis['last_month_change_pct'])}</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="fp-metric">
      <div class="fp-metric-label">Avg Monthly</div>
      <div class="fp-metric-val">{format_currency(analysis['avg_monthly'])}</div>
      <div class="fp-metric-sub">
        <span class="fp-badge fp-badge-grey">over {analysis['num_months']} months</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    pct = analysis['top_category_pct_total']
    st.markdown(f"""
    <div class="fp-metric">
      <div class="fp-metric-label">Top Category</div>
      <div class="fp-metric-val-sm">{analysis['top_category']}</div>
      <div class="fp-metric-sub">
        <span class="fp-badge fp-badge-red">{pct:.1f}% of total spend</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

with c4:
    pred_amt   = pred.get("predicted_amount", 0)
    conf_label = pred.get("confidence_label", "")
    conf_score = pred.get("confidence_score", 0)
    st.markdown(f"""
    <div class="fp-metric">
      <div class="fp-metric-label">Next Month Forecast</div>
      <div class="fp-metric-val" style="color:#D4A853;">{format_currency(pred_amt)}</div>
      <div class="fp-metric-sub">{badge_conf(conf_label, conf_score)}</div>
    </div>
    """, unsafe_allow_html=True)

# ── Charts ───────────────────────────────────────────────────────
st.markdown("<div style='height:1.2rem'></div>", unsafe_allow_html=True)
ch1, ch2 = st.columns(2)
with ch1:
    st.plotly_chart(
        chart_categories(analysis["category_totals"], analysis.get("category_pct_share")),
        use_container_width=True
    )
with ch2:
    st.plotly_chart(
        chart_monthly(analysis["monthly_totals"], analysis.get("monthly_mom_change")),
        use_container_width=True
    )


# ══════════════════════════════════════════════════════════════════
# ANOMALY INTELLIGENCE
# ══════════════════════════════════════════════════════════════════
st.markdown("""
<div class="fp-section-heading" style="margin-top:2.2rem;">
  <span class="fp-section-dot" style="background:#F43F5E; box-shadow:0 0 8px #F43F5E;"></span>
  Anomaly Intelligence
</div>
""", unsafe_allow_html=True)

if anom["has_anomalies"]:
    st.markdown(f"""
    <div class="fp-anomaly-warn">
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1.2rem;">
        <div>
          <div style="font-size:0.62rem; font-weight:700; color:#F43F5E; text-transform:uppercase;
            letter-spacing:0.1em; margin-bottom:0.3rem;">
            ⚠ Risk Alert &nbsp;—&nbsp; {anom['total_anomalies']} Anomaly(s) Detected
          </div>
          <div style="font-size:0.95rem; font-weight:500; color:#F0F6FF;">{anom['summary_text']}</div>
        </div>
        <div style="background:rgba(244,63,94,0.12); color:#F43F5E; font-size:1.6rem;
          width:50px; height:50px; display:flex; align-items:center; justify-content:center;
          border-radius:10px; border:1px solid rgba(244,63,94,0.22); flex-shrink:0;">⚠️</div>
      </div>
    """, unsafe_allow_html=True)

    for a in anom["monthly_anomalies"][:3]:
        d = "above" if a["pct_above_avg"] > 0 else "below"
        st.markdown(f"""
        <div class="fp-anomaly-row">
          <div>
            <div style="font-size:0.87rem; color:#F0F6FF; font-weight:600;">
              {a['month']} — Monthly Overspend</div>
            <div style="font-size:0.77rem; color:#7A8EAD; margin-top:3px;">
              ₹{a['amount']:,.0f} &nbsp;·&nbsp; {abs(a['pct_above_avg']):.0f}% {d} avg ₹{a['mean']:,.0f}
              &nbsp;·&nbsp; Z-score: {a['z_score']:.1f}
            </div>
          </div>
          {badge_sev(a['severity'])}
        </div>
        """, unsafe_allow_html=True)

    for a in anom["category_anomalies"][:4]:
        d = "above" if a["pct_above_avg"] > 0 else "below"
        st.markdown(f"""
        <div class="fp-anomaly-row">
          <div>
            <div style="font-size:0.87rem; color:#F0F6FF; font-weight:600;">
              {a['month']} — {a['category']} Spike</div>
            <div style="font-size:0.77rem; color:#7A8EAD; margin-top:3px;">
              ₹{a['amount']:,.0f} &nbsp;·&nbsp; {abs(a['pct_above_avg']):.0f}% {d} avg ₹{a['mean']:,.0f}
              &nbsp;·&nbsp; Z-score: {a['z_score']:.1f}
            </div>
          </div>
          {badge_sev(a['severity'])}
        </div>
        """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    pred_monthly = pred.get("monthly_data", [])
    if pred_monthly and anom["monthly_anomalies"]:
        st.plotly_chart(
            chart_anomaly(pred_monthly, anom["monthly_anomalies"]),
            use_container_width=True
        )
else:
    st.markdown("""
    <div class="fp-anomaly-ok">
      <div style="display:flex; align-items:center; gap:0.85rem;">
        <div style="font-size:1.6rem;">✅</div>
        <div>
          <div style="font-size:0.62rem; font-weight:700; color:#10B981; text-transform:uppercase;
            letter-spacing:0.1em; margin-bottom:0.2rem;">All Clear</div>
          <div style="font-size:0.9rem; color:#F0F6FF;">
            No spending anomalies detected. Your patterns look consistent.</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════
# ACTIONABLE INSIGHTS
# ══════════════════════════════════════════════════════════════════
st.markdown("""
<div class="fp-section-heading" style="margin-top:2.2rem;">
  <span class="fp-section-dot" style="background:#10B981; box-shadow:0 0 8px #10B981;"></span>
  Actionable Insights
</div>
""", unsafe_allow_html=True)

si1, si2 = st.columns([2, 1])

with si1:
    for s in suggestions["suggestions"]:
        pct_above = s.get("pct_above_all_avg", 0)
        pct_tag = f"+{pct_above:.0f}% vs avg" if pct_above > 0 else "Key area"
        st.markdown(f"""
        <div class="fp-suggest">
          <div style="display:flex; justify-content:space-between; align-items:flex-start;">
            <div style="flex:1;">
              <div style="font-size:0.62rem; font-weight:700; color:#3A4A65;
                text-transform:uppercase; letter-spacing:0.1em; margin-bottom:0.45rem;">
                {s['category']} &nbsp;·&nbsp;
                <span style="font-family:'JetBrains Mono',monospace;">
                  ₹{s['monthly_avg']:,.0f}/mo
                </span> &nbsp;·&nbsp;
                <span style="color:#F43F5E;">{pct_tag}</span>
              </div>
              <div style="font-size:0.92rem; color:#F0F6FF; font-weight:600; margin-bottom:0.3rem;">
                {s['insight']}</div>
              <div style="color:#7A8EAD; font-size:0.82rem; line-height:1.55;">{s['action']}</div>
            </div>
            <div style="background:rgba(16,185,129,0.1); color:#10B981;
              padding:0.3rem 0.9rem; border-radius:9999px; font-weight:700; font-size:0.76rem;
              border:1px solid rgba(16,185,129,0.22); white-space:nowrap;
              margin-left:1rem; margin-top:4px; font-family:'JetBrains Mono',monospace;">
              +{format_currency(s['estimated_saving'])}/mo
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

with si2:
    st.markdown(f"""
    <div class="fp-metric" style="text-align:center; padding:2.2rem 1.5rem;">
      <div class="fp-metric-label" style="text-align:center;">Monthly Recovery Potential</div>
      <div style="font-family:'JetBrains Mono',monospace; font-size:2.3rem; font-weight:500;
        color:#10B981; margin:0.7rem 0; letter-spacing:-0.03em; line-height:1;">
        {format_currency(suggestions['total_savings_potential'])}
      </div>
      <div style="font-size:0.78rem; color:#3A4A65; margin-bottom:1.2rem;">
        achievable per month
      </div>
      <div style="background:rgba(16,185,129,0.07); border:1px solid rgba(16,185,129,0.15);
        border-radius:8px; padding:0.7rem;">
        <div style="font-size:0.68rem; color:#10B981; font-weight:600; letter-spacing:0.04em;">
          Based on {suggestions['num_months']} months of history
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════
# EXPENSE FORECAST
# ══════════════════════════════════════════════════════════════════
st.markdown("""
<div class="fp-section-heading" style="margin-top:2.2rem;">
  <span class="fp-section-dot" style="background:#D4A853; box-shadow:0 0 8px #D4A853;"></span>
  Expense Forecast
</div>
""", unsafe_allow_html=True)

pred_monthly = pred.get("monthly_data", [])
if pred_monthly and not pred.get("error"):
    fc1, fc2 = st.columns([3, 1])
    with fc1:
        st.plotly_chart(
            chart_prediction(pred_monthly, pred["predicted_amount"], pred["next_month_label"]),
            use_container_width=True
        )
    with fc2:
        change_pct = pred["change_pct"]
        vs_avg_pct = pred.get("vs_avg_pct", 0)
        d_str   = "▲ More" if change_pct > 0 else "▼ Less"
        d_color = "#F43F5E" if change_pct > 0 else "#10B981"
        v_arrow = "▲" if vs_avg_pct > 0 else "▼"
        v_color = "#F43F5E" if vs_avg_pct > 0 else "#10B981"
        st.markdown(f"""
        <div class="fp-metric" style="height:100%; box-sizing:border-box;">
          <div class="fp-metric-label">Model</div>
          <div style="font-size:0.74rem; color:#7A8EAD; margin-bottom:1.2rem; line-height:1.6;
            font-family:'JetBrains Mono',monospace;">
            EMA (60%) +<br>Linear Regression (40%)
          </div>
          <div class="fp-metric-label">vs Last Month</div>
          <div style="font-size:1.3rem; font-weight:600; color:{d_color}; margin-bottom:1.1rem;
            font-family:'JetBrains Mono',monospace;">
            {d_str} &nbsp; {abs(change_pct):.1f}%
          </div>
          <div class="fp-metric-label">vs Historical Avg</div>
          <div style="font-size:1rem; color:{v_color}; margin-bottom:1.1rem;
            font-family:'JetBrains Mono',monospace;">
            {v_arrow} {abs(vs_avg_pct):.1f}%
          </div>
          <div class="fp-metric-label">Confidence</div>
          {badge_conf(pred['confidence_label'], pred['confidence_score'])}
        </div>
        """, unsafe_allow_html=True)
else:
    st.info(pred.get("error", "Not enough data for prediction — upload more months."))


# ══════════════════════════════════════════════════════════════════
# FINPILOT COPILOT — AI CHATBOT
# ══════════════════════════════════════════════════════════════════
st.markdown("""
<div class="fp-section-heading" style="margin-top:2.2rem;">
  <span class="fp-section-dot" style="background:#0F9D8C; box-shadow:0 0 8px #0F9D8C;
    animation: pulse-dot 2s infinite;"></span>
  FinPilot Copilot
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style="margin-bottom:1.6rem;">
  <div style="font-size:1rem; font-weight:700; color:#F0F6FF; margin-bottom:0.3rem;">
    Ask your financial AI agent anything...
  </div>
  <div style="font-size:0.82rem; color:#3A4A65; line-height:1.75;">
    <em>Try:</em> &nbsp;
    <span style="color:#7A8EAD;">"Where am I overspending?"</span> &nbsp;·&nbsp;
    <span style="color:#7A8EAD;">"How can I save money?"</span> &nbsp;·&nbsp;
    <span style="color:#7A8EAD;">"Did I have unusual expenses?"</span> &nbsp;·&nbsp;
    <span style="color:#7A8EAD;">"Predict my next month"</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Render chat history ──────────────────────────────────────────
for entry in st.session_state.chat_history:
    _q = entry["query"]
    _r = entry["result"]
    _routing = "🤖 LLM-Driven" if _r.get("llm_driven") else "🔑 Keyword Router"

    _tools_html = (
        " &rarr; ".join([
            f"<code style='background:rgba(15,157,140,0.1); color:#2DD4BF;"
            f"padding:2px 9px; border-radius:4px; font-size:0.8rem;"
            f"font-family:JetBrains Mono,monospace;'>{t}</code>"
            for t in _r["tools_used"]
        ]) or "<em>No tool</em>"
    )

    # Query bubble
    st.markdown(f"""
    <div class="fp-query-bubble">
      <div style="font-size:0.6rem; font-weight:700; color:#0F9D8C; text-transform:uppercase;
        letter-spacing:0.1em; margin-bottom:0.3rem;">Your Question</div>
      <div style="font-size:0.95rem; color:#F0F6FF; font-weight:500;">{_q}</div>
    </div>
    """, unsafe_allow_html=True)

    # Pipeline header
    st.markdown("""
    <div style="font-size:0.62rem; font-weight:700; color:#0F9D8C; text-transform:uppercase;
      letter-spacing:0.1em; margin: 0.8rem 0 0.55rem;">⚙️ &nbsp; Agent Execution Pipeline</div>
    """, unsafe_allow_html=True)

    # Intent + Tools
    st.markdown(f"""
    <div style="display:flex; gap:0.8rem; margin-bottom:0.5rem;">
      <div class="fp-pipeline-step" style="flex:1;">
        <div class="fp-pipe-label">① Intent Detected
          <span style="opacity:0.45; font-weight:400;"> — {_routing}</span>
        </div>
        <div class="fp-pipe-val">{_r['intent']}</div>
      </div>
      <div class="fp-pipeline-step" style="flex:1;">
        <div class="fp-pipe-label">② Tools Selected</div>
        <div class="fp-pipe-val">{_tools_html}</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Reasoning chain
    if _r["reasoning"]:
        reasoning_html = "".join(
            f'<div class="fp-reasoning-row">'
            f'<span class="fp-step-pill">Step {i}</span>'
            f'<span>{step}</span>'
            f'</div>'
            for i, step in enumerate(_r["reasoning"], 1)
        )
        st.markdown(f"""
        <div class="fp-pipeline-step" style="margin-bottom:0.5rem;">
          <div class="fp-pipe-label" style="margin-bottom:0.55rem;">③ Agent Reasoning Chain</div>
          {reasoning_html}
        </div>
        """, unsafe_allow_html=True)

    # Raw tool data — collapsed by default
    if _r.get("tool_summaries"):
        with st.expander("④ Raw Tool Observations — data passed to AI", expanded=False):
            for tname, summary in _r["tool_summaries"].items():
                st.markdown(f"**`{tname}`**")
                st.code(summary, language="text")

    # Final AI response
    st.markdown("""
    <div style="font-size:0.82rem; font-weight:700; color:#F0F6FF;
      margin: 1.1rem 0 0.45rem;">✨ &nbsp; AI Insight</div>
    """, unsafe_allow_html=True)
    st.info(_r["llm_response"])

    # Optional inline charts from agent tools
    _cd = _r.get("chart_data", {})
    if "prediction" in _cd and not _cd["prediction"].get("error"):
        _pd = _cd["prediction"]
        with st.expander("📈 View Prediction Chart", expanded=False):
            st.plotly_chart(
                chart_prediction(_pd["monthly_data"], _pd["predicted_amount"], _pd["next_month_label"]),
                use_container_width=True
            )
    if "anomaly" in _cd and _cd["anomaly"]["has_anomalies"]:
        _pm = pred.get("monthly_data", [])
        if _pm:
            with st.expander("⚠️ View Anomaly Chart", expanded=True):
                st.plotly_chart(
                    chart_anomaly(_pm, _cd["anomaly"]["monthly_anomalies"]),
                    use_container_width=True
                )

    st.markdown("""
    <hr style="border:none; border-top:1px solid rgba(255,255,255,0.05); margin:1.4rem 0;">
    """, unsafe_allow_html=True)


# ── Input bar ────────────────────────────────────────────────────
ci1, ci2 = st.columns([5, 1])
with ci1:
    user_query = st.text_input(
        "Query",
        placeholder="e.g. Where am I overspending this month?",
        label_visibility="collapsed",
        key=f"fp_query_{st.session_state.input_counter}"
    )
with ci2:
    run_btn = st.button("Run Agent ›", use_container_width=True, type="primary")

if run_btn and user_query.strip():
    with st.spinner("🤖 Agent is analyzing your data..."):
        result = run_agent(user_query.strip(), df)
    st.session_state.chat_history.append({"query": user_query.strip(), "result": result})
    st.session_state.input_counter += 1
    st.rerun()


# ══════════════════════════════════════════════════════════════════
# HOW IT WORKS  (shown after data is loaded too, at the bottom)
# ══════════════════════════════════════════════════════════════════
st.markdown("""
<div class="fp-section-heading" style="margin-top:3rem;">
  <span class="fp-section-dot" style="background:#0F9D8C; box-shadow:0 0 8px #0F9D8C;"></span>
  How FinPilot Works
</div>
""", unsafe_allow_html=True)

hw1, hw2, hw3, hw4 = st.columns(4)
steps2 = [
    ("01", "📂", "Upload CSV", "Drop in any expense CSV with date, category and amount."),
    ("02", "💬", "Ask Anything", "Natural language questions about your finances."),
    ("03", "🤖", "Agent Routes", "LLM planner selects tools. Tools run on your data."),
    ("04", "✨", "Get Insights", "Quantified, specific advice — not generic responses."),
]
for col, (num, icon, title, desc) in zip([hw1, hw2, hw3, hw4], steps2):
    with col:
        st.markdown(f"""
        <div class="fp-how-step">
          <div class="fp-how-num">{num}</div>
          <div style="font-size:1.4rem; margin-bottom:0.4rem;">{icon}</div>
          <div style="font-size:0.88rem; font-weight:700; color:#F0F6FF; margin-bottom:0.35rem;">{title}</div>
          <div style="font-size:0.76rem; color:#7A8EAD; line-height:1.55;">{desc}</div>
        </div>
        """, unsafe_allow_html=True)

# ── Footer ───────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center; padding:3rem 0 1rem;
  border-top:1px solid rgba(255,255,255,0.05); margin-top:3rem;">
  <div style="font-size:1rem; font-weight:800; color:#F0F6FF; margin-bottom:0.25rem;
    font-family:'Plus Jakarta Sans',sans-serif;">
    ✈️ FinPilot AI
  </div>
  <div style="font-size:0.78rem; color:#3A4A65;">
    Agentic Financial Assistant &nbsp;·&nbsp; Capstone Project &nbsp;·&nbsp; KIIT University
  </div>
</div>
""", unsafe_allow_html=True)
