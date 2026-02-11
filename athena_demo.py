import streamlit as st
import time
from datetime import datetime
import pandas as pd

# --- CONFIGURATION ---
st.set_page_config(page_title="Athena Hotel OS", page_icon="🏛️", layout="wide", initial_sidebar_state="collapsed")

# ======================================================
# 🧠 SHARED STATE (DATABASE SIMULATION)
# ======================================================
@st.cache_resource
class SharedState:
    def __init__(self):
        self.checks = {"ice": False, "fridge": False, "music": False, "glass": False}
        self.completion_time = None
        self.upsell_revenue = 0
        self.upsell_count = 0
        self.alert_log = [] 
        self.alert_id_counter = 0
        self.reviews_scanned = False
        self.latest_online_review = None 
        self.last_update = time.time()

    def add_alert(self, source, msg, priority="Normal"):
        self.alert_id_counter += 1
        timestamp = datetime.now().strftime('%H:%M')
        new_alert = {
            "id": self.alert_id_counter,
            "source": source,
            "msg": msg,
            "time": timestamp,
            "status": "Pending",
            "priority": priority
        }
        self.alert_log.append(new_alert)

def get_shared_state():
    return SharedState()

state = get_shared_state()

# --- LOCAL STATE ---
if 'search_done' not in st.session_state: st.session_state.search_done = False
if 'sold' not in st.session_state: st.session_state.sold = False

# --- CSS STYLING ---
st.markdown("""
<style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    .stTabs [data-baseweb="tab-list"] {gap: 10px; justify-content: center;}
    .stTabs [data-baseweb="tab"] {height: 45px; background-color: #f8f9fa; border-radius: 8px; font-weight: 600;}
    .stTabs [aria-selected="true"] {background-color: #FF4B4B !important; color: white !important;}
    .stButton>button {width: 100%; border-radius: 10px; height: 50px; font-weight: bold; box-shadow: 0px 1px 3px rgba(0,0,0,0.1);}
    
    .status-gm {padding: 12px; border-radius: 8px; background-color: #e8f5e9; border-left: 5px solid #2e7d32; color: #1b5e20; font-weight: bold; margin-bottom: 5px;}
    .warn-gm {padding: 12px; border-radius: 8px; background-color: #fff8e1; border-left: 5px solid #ffb300; color: #e65100; font-weight: bold; margin-bottom: 5px;}
    .alert-gm {padding: 12px; border-radius: 8px; background-color: #ffebee; border-left: 5px solid #c62828; color: #b71c1c; font-weight: bold; margin-bottom: 5px;}
    
    .alert-card {padding: 10px; margin-bottom: 8px; border-radius: 5px; background-color: #ffebee; border: 1px solid #ffcdd2; color: #b71c1c; font-size: 14px;}
    .critical-card {padding: 15px; margin-bottom: 8px; border-radius: 5px; background-color: #000; border: 2px solid #ff0000; color: #fff; font-size: 16px; animation: blinker 1.5s linear infinite;}
    @keyframes blinker { 50% { opacity: 0.5; } }
    
    .review-card {padding: 15px; border-radius: 8px; background-color: #e3f2fd; border: 1px solid #90caf9; margin-bottom: 10px; color: #0d47a1;}
    .context-label {font-size: 12px; color: #888; text-transform: uppercase; font-weight: 700; margin-bottom: 8px; margin-top: 5px;}
    .roi-box {padding: 15px; background: #2d3436; color: #00ff00; border-radius: 10px; font-family: 'Courier New', Courier, monospace; border: 1px solid #00ff00;}
</style>
""", unsafe_allow_html=True)

st.title("Athena OS 🏛️")

tab1, tab2, tab3 = st.tabs(["🍹 Pool Bar", "🛎️ Reception", "👔 Director"])

# ==========================================
# TAB 1: POOL BAR
# ==========================================
with tab1:
    st.subheader("Staff Operations")
    
    def update_state():
        state.last_update = time.time()
        chk_sum = sum(state.checks.values())
        state.completion_time = datetime.now().strftime("%H:%M") if chk_sum == 4 else None

    c1, c2 = st.columns(2)
    with c1:
        state.checks["ice"] = st.checkbox("🧊 Ice Machine", value=state.checks["ice"], on_change=update_state)
        state.checks["fridge"] = st.checkbox("🌡️ Fridge OK", value=state.checks["fridge"], on_change=update_state)
    with c2:
        state.checks["music"] = st.checkbox("🎵 Music ON", value=state.checks["music"], on_change=update_state)
        state.checks["glass"] = st.checkbox("🍷 Glassware", value=state.checks["glass"], on_change=update_state)

    st.markdown("---")
    st.write("**⚠️ Issue Reporting**")
    msg_val = st.text_input("Report to Management:", key="pool_manual_input")

    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("Send Alert"):
            if msg_val:
                state.add_alert("POOL BAR", msg_val)
                st.toast("Alert Logged", icon="📨")
    with col_btn2:
        if st.button("🚨 CRITICAL ISSUE"):
            state.add_alert("POOL BAR", "EMERGENCY: WATER LEAK NEAR ELECTRICAL", priority="High")
            st.toast("CRITICAL ALERT SENT", icon="🔥")

# ==========================================
# TAB 2: RECEPTION
# ==========================================
with tab2:
    st.subheader("Front Desk")
    if st.button("🔍 Search Booking #4052"):
        st.session_state.search_done = True
        st.toast("Guest Found: John Doe", icon="👤")

    if st.session_state.search_done:
        k1, k2 = st.columns(2)
        k1.metric("Current Rate", "100€")
        k2.metric("Suite Upgrade", "150€", delta="+50€")
        
        if st.button("✅ Confirm Upgrade (+50€)"):
            state.upsell_revenue += 50
            state.upsell_count += 1
            state.last_update = time.time()
            st.session_state.sold = True
            st.balloons()

# ==========================================
# TAB 3: GM DASHBOARD
# ==========================================
with tab3:
    selected_hotel = st.selectbox("Group Overview:", ["CHC Galini Sea View", "CHC Athina Palace", "CHC Royal Palace", "CHC Sea Side"])
    st.caption(f"Connected to Unified Cloud Interface for {selected_hotel}")
    
    col_gm_left, col_gm_right = st.columns([1.2, 1.5]) 

    with col_gm_left:
        st.markdown('<div class="context-label">DEPARTMENT STATUS</div>', unsafe_allow_html=True)
        reception_style = "status-gm" if state.upsell_revenue > 0 else "warn-gm"
        st.markdown(f'<div class="{reception_style}">🛎️ RECEPTION: {state.upsell_revenue}€ UPSOLD TODAY</div>', unsafe_allow_html=True)
        
        cnt = sum(state.checks.values())
        if cnt == 4: st.markdown(f'<div class="status-gm">🍹 POOL BAR: READY ({state.completion_time})</div>', unsafe_allow_html=True)
        elif cnt > 0: st.markdown(f'<div class="warn-gm">🍹 POOL BAR: SETTING UP ({cnt}/4)</div>', unsafe_allow_html=True)
        else: st.markdown('<div class="alert-gm">🍹 POOL BAR: PENDING SETUP</div>', unsafe_allow_html=True)
            
        st.divider()
        
        st.markdown('<div class="context-label">FINANCIAL INTELLIGENCE</div>', unsafe_allow_html=True)
        st.metric("Total Upsell", f"{state.upsell_revenue}€")
        
        if state.upsell_revenue > 0:
            annual_impact = state.upsell_revenue * 180 
            st.markdown(f"""
            <div class="roi-box">
                <b>Athena AI Projection:</b><br>
                EST. ANNUAL IMPACT: +{annual_impact:,}€<br>
                <small style="color:#00ff0077">Based on current conversion rate.</small>
            </div>
            """, unsafe_allow_html=True)

    with col_gm_right:
        st.markdown('<div class="context-label">⚠️ ACTIVE ISSUES</div>', unsafe_allow_html=True)
        pending_alerts = [a for a in state.alert_log if a['status'] == "Pending"]
        
        for alert in pending_alerts:
            card_class = "critical-card" if alert['priority'] == "High" else "alert-card"
            st.markdown(f'<div class="{card_class}"><b>{alert["source"]}</b>: {alert["msg"]}</div>', unsafe_allow_html=True)
            if st.button(f"Resolve ID: {alert['id']}", key=f"res_{alert['id']}"):
                alert['status'] = "Acknowledged"
                st.rerun()

        st.divider()
        
        if st.button("📋 Generate Smart Handover Report"):
            st.info(f"**Athena Executive Summary:** Today's ops show {state.upsell_count} successful upsells. Pool Bar setup completed at {state.completion_time}. All critical issues resolved. Group EBITDA trend: Positive.")

        st.divider()
        st.markdown('<div class="context-label">✨ AI REPUTATION MONITOR</div>', unsafe_allow_html=True)
        if st.button("🔄 Sync Reviews"):
            state.reviews_scanned = True
            state.latest_online_review = {"source": "Booking.com", "guest": "John D.", "text": "The pool bar staff was excellent but the ice machine was noisy."}
        
        if state.reviews_scanned:
            st.markdown(f'<div class="review-card"><i>"{state.latest_online_review["text"]}"</i></div>', unsafe_allow_html=True)
            st.success(f"🤖 Athena Suggestion: Draft reply generated.")

time.sleep(2)
st.rerun()