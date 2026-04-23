"""
dashboard/app.py — Options Pricing & Risk Dashboard
UI: Dark slate + electric blue. NO sidebar. Top nav + horizontal tabs.
Fonts: Playfair Display + Inconsolata.
"""

import sys
import numpy as np
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

st.set_page_config(page_title="Options Risk Desk", page_icon="⚡",
                   layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700;900&family=Inconsolata:wght@300;400;500;700&display=swap');
:root {
    --bg:#0a0e1a; --panel:#0f1628; --card:#131c30; --border:#1e2d4a;
    --blue:#2979ff; --blue2:#82b1ff; --gold:#ffd54f;
    --white:#e8eeff; --muted:#4a5878; --red:#ff5252; --green:#69f0ae; --text:#c8d4f0;
}
html,body,[data-testid="stAppViewContainer"],[data-testid="stApp"]{
    background:var(--bg)!important; font-family:'Inconsolata',monospace!important; color:var(--text)!important;
}
[data-testid="stSidebar"],[data-testid="collapsedControl"],button[kind="header"]{display:none!important;}
.main .block-container{max-width:100%!important; padding:0 2rem 2rem 2rem!important;}
.topnav{background:var(--panel);border-bottom:1px solid var(--border);
    padding:0 2rem;display:flex;align-items:center;gap:0;
    margin:0 -2rem 2rem -2rem;}
.topnav-brand{font-family:'Playfair Display',serif;font-size:1.1rem;font-weight:900;
    color:var(--white);letter-spacing:.08em;padding:16px 32px 16px 0;
    border-right:1px solid var(--border);margin-right:8px;white-space:nowrap;}
.topnav-brand span{color:var(--blue);}
.kpi{background:var(--card);border:1px solid var(--border);
    border-top:2px solid var(--blue);padding:14px 16px;margin:4px 0;}
.kpi.gold{border-top-color:var(--gold);} .kpi.green{border-top-color:var(--green);}
.kpi.red{border-top-color:var(--red);}
.kpi-label{font-size:9px;letter-spacing:.2em;color:var(--muted);text-transform:uppercase;margin-bottom:6px;}
.kpi-value{font-family:'Playfair Display',serif;font-size:1.5rem;color:var(--white);line-height:1.1;}
.kpi-sub{font-size:10px;color:var(--muted);margin-top:4px;}
h1{font-family:'Playfair Display',serif!important;font-size:2rem!important;
    font-weight:900!important;color:var(--white)!important;margin-bottom:8px!important;}
h2{font-family:'Playfair Display',serif!important;color:var(--white)!important;font-size:1.1rem!important;}
h3{font-family:'Inconsolata',monospace!important;font-size:.72rem!important;
    letter-spacing:.22em!important;text-transform:uppercase!important;
    color:var(--muted)!important;font-weight:500!important;}
div[data-testid="metric-container"]{background:var(--card)!important;
    border:1px solid var(--border)!important;border-top:2px solid var(--blue)!important;
    padding:14px!important;border-radius:0!important;}
div[data-testid="metric-container"] label{font-size:9px!important;
    letter-spacing:.2em!important;text-transform:uppercase!important;
    color:var(--muted)!important;font-family:'Inconsolata',monospace!important;}
div[data-testid="metric-container"] [data-testid="stMetricValue"]{
    font-family:'Playfair Display',serif!important;font-size:1.5rem!important;color:var(--white)!important;}
.stTabs [data-baseweb="tab"]{font-family:'Inconsolata',monospace!important;
    font-size:11px!important;letter-spacing:.15em!important;text-transform:uppercase!important;
    color:var(--muted)!important;background:transparent!important;
    border-bottom:2px solid transparent!important;padding:10px 20px!important;}
.stTabs [aria-selected="true"]{color:var(--blue2)!important;border-bottom:2px solid var(--blue)!important;}
.stTabs [data-baseweb="tab-list"]{border-bottom:1px solid var(--border)!important;
    background:transparent!important;gap:4px!important;}
.stButton>button{background:var(--blue)!important;color:white!important;border:none!important;
    font-family:'Inconsolata',monospace!important;letter-spacing:.12em!important;
    text-transform:uppercase!important;font-size:11px!important;
    padding:10px 28px!important;border-radius:0!important;}
.stButton>button:hover{background:var(--blue2)!important;color:var(--bg)!important;}
[data-testid="stNumberInput"] input,[data-testid="stSelectbox"]>div>div{
    background:var(--card)!important;border:1px solid var(--border)!important;
    border-radius:0!important;color:var(--white)!important;}
p,li{color:var(--text)!important;}
</style>""", unsafe_allow_html=True)

BG=PANEL="#0f1628"; CARD="#131c30"; BLUE="#2979ff"; BLUE2="#82b1ff"
GOLD="#ffd54f"; RED="#ff5252"; GREEN="#69f0ae"; MUTED="#4a5878"; WHITE="#e8eeff"

PLOT = dict(
    paper_bgcolor=CARD, plot_bgcolor=CARD,
    font=dict(family="Inconsolata", color=WHITE, size=11),
    xaxis=dict(gridcolor="#1e2d4a", linecolor="#1e2d4a", tickfont=dict(size=10,color=MUTED)),
    yaxis=dict(gridcolor="#1e2d4a", linecolor="#1e2d4a", tickfont=dict(size=10,color=MUTED)),
    legend=dict(bgcolor="#0f1628", bordercolor="#1e2d4a", borderwidth=1, font=dict(size=10)),
    margin=dict(l=50,r=20,t=48,b=40),
)

st.markdown("""
<div class="topnav">
  <div class="topnav-brand">OPTIONS <span>RISK</span> DESK &nbsp;|&nbsp;
  <span style="font-size:.75rem;font-weight:400;color:#4a5878;letter-spacing:.15em">
  QUANTITATIVE ANALYTICS</span></div>
</div>""", unsafe_allow_html=True)

with st.expander("⚙  Global Parameters", expanded=True):
    c1,c2,c3,c4,c5,c6,c7 = st.columns(7)
    S     = c1.number_input("Spot (S)",     1.0, 2000.0, 100.0, 1.0)
    K     = c2.number_input("Strike (K)",   1.0, 2000.0, 100.0, 1.0)
    T     = c3.number_input("Expiry (Yrs)", 0.01,  5.0,    1.0, 0.01)
    r     = c4.number_input("Rate (r)",     0.0,   0.2,   0.05, 0.005, format="%.3f")
    sigma = c5.number_input("Vol (σ)",      0.01,  2.0,   0.20, 0.01,  format="%.3f")
    q     = c6.number_input("Div Yield",    0.0,   0.2,   0.0,  0.005, format="%.3f")
    otype = c7.selectbox("Type", ["call","put"])

from pricing.black_scholes import BlackScholes, OptionParams, build_vol_surface
from pricing.monte_carlo   import price_european, price_asian, price_barrier
from pricing.risk_metrics  import (generate_portfolio_returns, historical_var,
                                    parametric_var, conditional_var, scenario_pnl)

def BS(): return BlackScholes(OptionParams(S,K,T,r,sigma,otype,q))

tab1,tab2,tab3,tab4,tab5 = st.tabs([
    "⚡  Pricer & Greeks",
    "🌊  Vol Surface",
    "🎲  Monte Carlo",
    "📉  Risk & VaR",
    "🔥  Greeks Heatmap",
])

# ── TAB 1 — PRICER ──────────────────────────────────────────────────────────
with tab1:
    bs = BS(); g = bs.all_greeks()
    intrinsic = max(S-K,0) if otype=="call" else max(K-S,0)
    time_val  = g["price"] - intrinsic
    moneyness = "ATM" if abs(S/K-1)<0.02 else (
                "ITM" if (S>K and otype=="call") or (S<K and otype=="put") else "OTM")

    row1 = st.columns(6)
    kpis1 = [("Theo Price",f"${g['price']:.4f}","blue",""),
             ("Intrinsic", f"${intrinsic:.4f}","gold",""),
             ("Time Value",f"${time_val:.4f}","green",""),
             ("Moneyness", moneyness,"gold",""),
             ("Delta  Δ",  f"{g['delta']:.4f}","blue",""),
             ("Gamma  Γ",  f"{g['gamma']:.6f}","blue","")]
    for col,(lbl,val,clr,sub) in zip(row1,kpis1):
        col.markdown(f'<div class="kpi {clr}"><div class="kpi-label">{lbl}</div>'
                     f'<div class="kpi-value">{val}</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    row2 = st.columns(6)
    kpis2 = [("Theta Θ/day",f"{g['theta']:.4f}","red",""),
             ("Vega   ν",   f"{g['vega']:.4f}","blue","per 1% vol"),
             ("Rho    ρ",   f"{g['rho']:.4f}","blue","per 1% rate"),
             ("Vol σ",      f"{sigma:.1%}","gold","annualized"),
             ("Expiry",     f"{T:.2f}Y","green",f"≈{int(T*252)}d"),
             ("Rate r",     f"{r:.2%}","blue","risk-free")]
    for col,(lbl,val,clr,sub) in zip(row2,kpis2):
        col.markdown(f'<div class="kpi {clr}"><div class="kpi-label">{lbl}</div>'
                     f'<div class="kpi-value">{val}</div>'
                     f'<div class="kpi-sub">{sub}</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col1,col2 = st.columns(2)

    with col1:
        st.subheader("Price & Delta vs Spot")
        spots  = np.linspace(S*0.5, S*1.5, 120)
        prices = [BlackScholes(OptionParams(s,K,T,r,sigma,otype,q)).price() for s in spots]
        deltas = [BlackScholes(OptionParams(s,K,T,r,sigma,otype,q)).delta() for s in spots]
        fig = make_subplots(specs=[[{"secondary_y":True}]])
        fig.add_trace(go.Scatter(x=spots,y=prices,name="Price",
                                  line=dict(color=BLUE2,width=2.5)),secondary_y=False)
        fig.add_trace(go.Scatter(x=spots,y=deltas,name="Delta",
                                  line=dict(color=GOLD,width=1.5,dash="dot")),secondary_y=True)
        fig.add_vline(x=S,line_color=GREEN,line_dash="dash",
                      annotation_text="Spot",annotation_font=dict(color=GREEN,size=10))
        fig.add_vline(x=K,line_color=RED,line_dash="dash",
                      annotation_text="Strike",annotation_font=dict(color=RED,size=10))
        fig.update_layout(**PLOT,height=340,
                          title=dict(text="PRICE & DELTA vs SPOT",font=dict(size=10,color=MUTED)))
        fig.update_yaxes(title_text="Price ($)",secondary_y=False)
        fig.update_yaxes(title_text="Delta",secondary_y=True)
        st.plotly_chart(fig,use_container_width=True)

    with col2:
        st.subheader("Time Decay")
        expiries = np.linspace(0.02, 2.5, 100)
        p_c = [BlackScholes(OptionParams(S,K,t,r,sigma,"call",q)).price() for t in expiries]
        p_p = [BlackScholes(OptionParams(S,K,t,r,sigma,"put", q)).price() for t in expiries]
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=expiries,y=p_c,name="Call",
                                   line=dict(color=GREEN,width=2),
                                   fill="tozeroy",fillcolor="rgba(105,240,174,0.05)"))
        fig2.add_trace(go.Scatter(x=expiries,y=p_p,name="Put",
                                   line=dict(color=RED,width=2),
                                   fill="tozeroy",fillcolor="rgba(255,82,82,0.05)"))
        fig2.add_vline(x=T,line_color=GOLD,line_dash="dash",
                       annotation_text="Now",annotation_font=dict(color=GOLD))
        fig2.update_layout(**PLOT,height=340,
                           title=dict(text="TIME VALUE DECAY",font=dict(size=10,color=MUTED)),
                           xaxis_title="Time to Expiry (Years)",yaxis_title="Price ($)")
        st.plotly_chart(fig2,use_container_width=True)

# ── TAB 2 — VOL SURFACE ──────────────────────────────────────────────────────
with tab2:
    st.title("Volatility Surface")
    np.random.seed(42)
    expiries_v = [0.1,0.25,0.5,0.75,1.0,1.5,2.0]
    strikes_v  = np.linspace(S*0.70, S*1.30, 15)
    surface    = build_vol_surface(S, r, expiries_v, strikes_v, otype, q)

    col1,col2 = st.columns([3,2])
    with col1:
        fig = go.Figure(data=[go.Surface(
            x=strikes_v, y=expiries_v, z=surface*100,
            colorscale=[[0,PANEL],[0.4,BLUE],[0.7,BLUE2],[1,WHITE]],
            showscale=True,
            colorbar=dict(
                title=dict(text="IV (%)", font=dict(color=WHITE,size=10)),
                tickfont=dict(size=9,color=WHITE)
            )
        )])
        fig.update_layout(
            paper_bgcolor=CARD,
            scene=dict(
                xaxis=dict(title="Strike",backgroundcolor=CARD,
                           gridcolor="#1e2d4a",tickfont=dict(color=WHITE)),
                yaxis=dict(title="Expiry (Y)",backgroundcolor=CARD,
                           gridcolor="#1e2d4a",tickfont=dict(color=WHITE)),
                zaxis=dict(title="IV (%)",backgroundcolor=CARD,
                           gridcolor="#1e2d4a",tickfont=dict(color=WHITE)),
            ),
            height=440, margin=dict(l=0,r=0,t=40,b=0),
            title=dict(text="3D IMPLIED VOLATILITY SURFACE",font=dict(size=10,color=MUTED))
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        ei = st.selectbox("Vol Smile — Expiry", range(len(expiries_v)),
                           format_func=lambda i: f"{expiries_v[i]}Y")
        smile = surface[ei]*100
        atm_i = np.argmin(np.abs(strikes_v - S))
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=strikes_v, y=smile, mode="lines+markers",
                                   line=dict(color=BLUE2,width=2),
                                   marker=dict(size=7,color=GOLD,
                                               line=dict(color=BLUE,width=1))))
        fig2.add_vline(x=S,line_color=GREEN,line_dash="dash",
                       annotation_text="ATM",annotation_font=dict(color=GREEN))
        fig2.update_layout(**PLOT,height=210,
                           title=dict(text=f"VOL SMILE — T={expiries_v[ei]}Y",
                                      font=dict(size=10,color=MUTED)),
                           xaxis_title="Strike",yaxis_title="IV (%)")
        st.plotly_chart(fig2, use_container_width=True)

        atm_vols = [surface[i][atm_i]*100 for i in range(len(expiries_v))]
        fig3 = go.Figure(go.Scatter(x=expiries_v,y=atm_vols,mode="lines+markers",
                                     line=dict(color=GOLD,width=2),
                                     marker=dict(size=8,color=GOLD),
                                     fill="tozeroy",fillcolor="rgba(255,213,79,0.06)"))
        fig3.update_layout(**PLOT,height=210,
                           title=dict(text="ATM TERM STRUCTURE",font=dict(size=10,color=MUTED)),
                           xaxis_title="Expiry (Years)",yaxis_title="ATM IV (%)")
        st.plotly_chart(fig3, use_container_width=True)

# ── TAB 3 — MONTE CARLO ──────────────────────────────────────────────────────
with tab3:
    st.title("Monte Carlo Simulation")
    col1,col2,col3 = st.columns([1,1,3])
    with col1:
        n_paths  = st.selectbox("Paths",[1000,5000,10000,50000],index=2)
        mc_model = st.selectbox("Model",["European","Asian","Barrier"])
    with col2:
        barrier,b_type = None,"down-and-out"
        if mc_model == "Barrier":
            barrier = st.number_input("Barrier",1.0,S*1.5,S*0.85,1.0)
            b_type  = st.selectbox("Type",["down-and-out","up-and-out",
                                            "down-and-in","up-and-in"])
        run_mc = st.button("▶  Run Simulation")

    if run_mc:
        with st.spinner("Simulating paths..."):
            kw = dict(S=S,K=K,T=T,r=r,sigma=sigma,option_type=otype,n_paths=n_paths)
            if   mc_model=="European": res = price_european(**kw)
            elif mc_model=="Asian":    res = price_asian(**kw)
            else:                      res = price_barrier(**kw,barrier=barrier,barrier_type=b_type)
            st.session_state["mc"] = res

    if "mc" in st.session_state:
        res = st.session_state["mc"]
        bs_p = BS().price()
        c1,c2,c3,c4 = st.columns(4)
        c1.metric("MC PRICE",  f"${res.price:.4f}")
        c2.metric("BS PRICE",  f"${bs_p:.4f}")
        c3.metric("DIFF",      f"${abs(res.price-bs_p):.5f}")
        c4.metric("STD ERROR", f"${res.std_error:.6f}")
        st.metric("95% CI", f"[ ${res.confidence_low:.4f}  —  ${res.confidence_high:.4f} ]")

        paths  = res.paths[:100]
        t_axis = np.linspace(0, T, paths.shape[1])
        fig = go.Figure()
        for i,path in enumerate(paths):
            fig.add_trace(go.Scatter(
                x=t_axis, y=path, mode="lines", showlegend=False,
                line=dict(color=f"rgba(41,121,255,{0.04 if i<90 else 0.9})",
                          width=0.7 if i<90 else 2.5)
            ))
        fig.add_hline(y=K,line_color=RED,line_dash="dash",
                      annotation_text=f"Strike K={K}",annotation_font=dict(color=RED))
        if barrier:
            fig.add_hline(y=barrier,line_color=GOLD,line_dash="dot",
                          annotation_text=f"Barrier={barrier}",annotation_font=dict(color=GOLD))
        fig.update_layout(**PLOT,height=400,
                          title=dict(text=f"SIMULATED PATHS — {mc_model.upper()} ({n_paths:,} paths)",
                                     font=dict(size=10,color=MUTED)),
                          xaxis_title="Time (Years)",yaxis_title="Asset Price ($)")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Configure parameters above and click **▶ Run Simulation**")

# ── TAB 4 — RISK & VAR ───────────────────────────────────────────────────────
with tab4:
    st.title("Risk & VaR Analysis")
    conf = st.slider("Confidence Level",0.90,0.99,0.95,0.01)

    positions = [
        {"S":S,"K":K,      "T":T,     "r":r,"sigma":sigma,     "option_type":otype,"q":q,"quantity":10},
        {"S":S,"K":K*0.95, "T":T*0.5, "r":r,"sigma":sigma*1.1, "option_type":"put","q":q,"quantity":5},
        {"S":S,"K":K*1.05, "T":T*1.5, "r":r,"sigma":sigma*0.9, "option_type":"call","q":q,"quantity":8},
    ]
    returns = generate_portfolio_returns(positions, n_days=500)
    hvar = historical_var(returns, conf)
    pvar = parametric_var(returns, conf)
    cvar = conditional_var(returns, conf)

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("HISTORICAL VaR", f"${hvar:.2f}", f"@{conf:.0%}")
    c2.metric("PARAMETRIC VaR", f"${pvar:.2f}", f"@{conf:.0%}")
    c3.metric("CVaR (ES)",       f"${cvar:.2f}", "Expected Shortfall")
    c4.metric("DAILY P&L VOL",  f"${returns.std():.2f}")

    col1,col2 = st.columns(2)
    with col1:
        fig = go.Figure()
        fig.add_trace(go.Histogram(x=returns,nbinsx=60,
                                    marker_color=BLUE,opacity=0.7,name="P&L"))
        fig.add_vline(x=-hvar,line_color=RED,line_width=2,
                      annotation_text=f"VaR {conf:.0%}",
                      annotation_font=dict(color=RED,size=10))
        fig.add_vline(x=-cvar,line_color=GOLD,line_width=2,line_dash="dash",
                      annotation_text="CVaR",annotation_font=dict(color=GOLD,size=10))
        fig.update_layout(**PLOT,height=330,showlegend=False,
                          title=dict(text="PORTFOLIO P&L DISTRIBUTION",font=dict(size=10,color=MUTED)),
                          xaxis_title="Daily P&L ($)",yaxis_title="Frequency")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        cum  = np.cumsum(returns)
        peak = np.maximum.accumulate(cum)
        dd   = cum - peak
        fig2 = make_subplots(rows=2,cols=1,shared_xaxes=True,row_heights=[0.65,0.35])
        fig2.add_trace(go.Scatter(x=list(range(len(cum))),y=cum,
                                   line=dict(color=BLUE2,width=2),name="Cum P&L"),row=1,col=1)
        fig2.add_trace(go.Scatter(x=list(range(len(dd))),y=dd,
                                   line=dict(color=RED,width=1),
                                   fill="tozeroy",fillcolor="rgba(255,82,82,0.12)",
                                   name="Drawdown"),row=2,col=1)
        fig2.update_layout(**PLOT,height=330,
                           title=dict(text="CUMULATIVE P&L + DRAWDOWN",font=dict(size=10,color=MUTED)))
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("P&L Scenario Grid — Spot × Volatility")
    spots_s,vols_s,grid = scenario_pnl(S,K,T,r,sigma,otype,10)
    fig3 = go.Figure(go.Heatmap(
        x=np.round(spots_s,1), y=np.round(vols_s*100,1), z=grid,
        colorscale=[[0,RED],[0.5,"#131c30"],[1,GREEN]],
        zmid=0, showscale=True,
        colorbar=dict(
            title=dict(text="P&L ($)", font=dict(color=WHITE,size=10)),
            tickfont=dict(size=9,color=WHITE)
        )
    ))
    fig3.add_vline(x=S,    line_color=WHITE,line_dash="dash",line_width=1)
    fig3.add_hline(y=sigma*100,line_color=GOLD,line_dash="dash",line_width=1)
    fig3.update_layout(**PLOT,height=360,
                       title=dict(text="SCENARIO ANALYSIS — P&L GRID",font=dict(size=10,color=MUTED)),
                       xaxis_title="Spot Price ($)",yaxis_title="Volatility (%)")
    st.plotly_chart(fig3, use_container_width=True)

# ── TAB 5 — GREEKS HEATMAP ───────────────────────────────────────────────────
with tab5:
    st.title("Greeks Heatmap")
    gc1,gc2 = st.columns([3,1])
    with gc2:
        greek = st.selectbox("Greek",["delta","gamma","theta","vega","rho"])

    spots_h = np.linspace(S*0.60, S*1.40, 35)
    vols_h  = np.linspace(0.05, 0.60, 28)
    grid_h  = np.zeros((len(vols_h), len(spots_h)))
    for i,v in enumerate(vols_h):
        for j,s in enumerate(spots_h):
            grid_h[i,j] = getattr(
                BlackScholes(OptionParams(s,K,T,r,v,otype,q)), greek
            )()

    with gc1:
        fig = go.Figure(go.Heatmap(
            x=np.round(spots_h,1), y=np.round(vols_h*100,1), z=grid_h,
            colorscale=[[0,RED],[0.35,"#131c30"],[0.65,BLUE],[1,BLUE2]],
            zmid=0, showscale=True,
            colorbar=dict(
                title=dict(text=greek.capitalize(), font=dict(color=WHITE,size=10)),
                tickfont=dict(size=9,color=WHITE)
            )
        ))
        fig.add_vline(x=S,line_color=GOLD,line_width=2,line_dash="dash",
                      annotation_text="Spot",annotation_font=dict(color=GOLD))
        fig.add_vline(x=K,line_color=WHITE,line_width=1,line_dash="dot",
                      annotation_text="Strike",annotation_font=dict(color=WHITE,size=9))
        fig.add_hline(y=sigma*100,line_color=GREEN,line_width=2,line_dash="dash",
                      annotation_text="σ",annotation_font=dict(color=GREEN))
        fig.update_layout(**PLOT,height=500,
                          title=dict(text=f"{greek.upper()} SENSITIVITY · SPOT × VOLATILITY",
                                     font=dict(size=10,color=MUTED)),
                          xaxis_title="Spot Price ($)",yaxis_title="Volatility (%)")
        st.plotly_chart(fig, use_container_width=True)

    with gc2:
        bs = BS(); greeks = bs.all_greeks()
        st.subheader("Live Greeks")
        for gname,gval in greeks.items():
            color = GREEN if (isinstance(gval,float) and gval>0)                     else RED if (isinstance(gval,float) and gval<0) else BLUE2
            st.markdown(f"""
            <div style="background:#131c30;border:1px solid #1e2d4a;
                border-left:3px solid {color};padding:10px 14px;margin:6px 0;">
              <div style="font-size:9px;letter-spacing:.2em;color:#4a5878;text-transform:uppercase">{gname}</div>
              <div style="font-family:'Playfair Display',serif;font-size:1.3rem;color:{color}">{gval}</div>
            </div>""", unsafe_allow_html=True)
