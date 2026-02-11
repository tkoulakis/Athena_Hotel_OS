import streamlit as st
import time
from datetime import datetime
import pandas as pd # Χρειαζόμαστε pandas για την προβολή του πίνακα ιστορικού

# --- CONFIGURATION ---
st.set_page_config(page_title="Athena Hotel OS", page_icon="🏛️", layout="wide", initial_sidebar_state="collapsed")

# ======================================================
# 🧠 SHARED STATE (DATABASE SIMULATION)
# ======================================================
@st.cache_resource
class SharedState:
    def __init__(self):
        # Checklist Data (Pool Bar)
        self.checks = {"ice": False, "fridge": False, "music": False, "glass": False}
        self.completion_time = None
        
        # Revenue Data
        self.upsell_revenue = 0
        self.last_transaction = "None"
        
        # --- ALERTS LOG SYSTEM (Priority Log) ---
        self.alert_log = [] 
        self.alert_id_counter = 0
        
        # --- REVIEWS INTELLIGENCE ---
        self.reviews_scanned = False
        self.latest_online_review = None 
        
        self.last_update = time.time()

    def add_alert(self, source, msg):
        self.alert_id_counter += 1
        timestamp = datetime.now().strftime('%H:%M')
        new_alert = {
            "id": self.alert_id_counter,
            "source": source,
            "msg": msg,
            "time": timestamp,
            "status": "Pending" # Pending -> Acknowledged
        }
        self.alert_log.append(new_alert)

def get_shared_state():
    return SharedState()

state = get_shared_state()

# --- LOCAL STATE ---
if 'search_done' not in st.session_state:
    st.session_state.search_done = False
if 'sold' not in st.session_state:
    st.session_state.sold = False

# --- CSS STYLING ---
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .stTabs [data-baseweb="tab-list"] {gap: 10px; justify-content: center;}
    .stTabs [data-baseweb="tab"] {height: 45px; background-color: #f8f9fa; border-radius: 8px; font-weight: 600;}
    .stTabs [aria-selected="true"] {background-color: #FF4B4B !important; color: white !important;}
    
    .stButton>button {width: 100%; border-radius: 10px; height: 50px; font-weight: bold; border: none; box-shadow: 0px 1px 3px rgba(0,0,0,0.1);}
    
    /* Department Status Bars */
    .status-gm {padding: 12px; border-radius: 8px; background-color: #e8f5e9; border-left: 5px solid #2e7d32; color: #1b5e20; font-weight: bold; margin-bottom: 5px;}
    .warn-gm {padding: 12px; border-radius: 8px; background-color: #fff8e1; border-left: 5px solid #ffb300; color: #e65100; font-weight: bold; margin-bottom: 5px;}
    .alert-gm {padding: 12px; border-radius: 8px; background-color: #ffebee; border-left: 5px solid #c62828; color: #b71c1c; font-weight: bold; margin-bottom: 5px;}
    
    /* Alert Cards in Dashboard */
    .alert-card {
        padding: 10px; margin-bottom: 8px; border-radius: 5px; 
        background-color: #ffebee; border: 1px solid #ffcdd2; 
        color: #b71c1c; font-size: 14px;
    }
    
    /* Review Card */
    .review-card {
        padding: 15px; border-radius: 8px; background-color: #e3f2fd; border: 1px solid #90caf9; margin-bottom: 10px; color: #0d47a1;
    }
    
    .context-label {font-size: 12px; color: #888; text-transform: uppercase; font-weight: 700; margin-bottom: 8px; margin-top: 5px;}
</style>
""", unsafe_allow_html=True)

st.title("Athena OS 🏛️")

# Tabs
tab1, tab2, tab3 = st.tabs(["🍹 Pool Bar", "🛎️ Reception", "👔 Director"])

# ==========================================
# TAB 1: POOL BAR (GENERATING ALERTS)
# ==========================================
with tab1:
    st.subheader("Staff Operations")
    
    # Checklist Logic
    def update_state():
        state.last_update = time.time()
        chk_sum = sum(state.checks.values())
        if chk_sum == 4 and state.completion_time is None:
             state.completion_time = datetime.now().strftime("%H:%M")
        elif chk_sum < 4:
             state.completion_time = None

    c1, c2 = st.columns(2)
    with c1:
        state.checks["ice"] = st.checkbox("🧊 Ice Machine", value=state.checks["ice"], on_change=update_state)
        state.checks["fridge"] = st.checkbox("🌡️ Fridge OK", value=state.checks["fridge"], on_change=update_state)
    with c2:
        state.checks["music"] = st.checkbox("🎵 Music ON", value=state.checks["music"], on_change=update_state)
        state.checks["glass"] = st.checkbox("🍷 Glassware", value=state.checks["glass"], on_change=update_state)

    st.markdown("---")
    
    # --- MANUAL ALERT ONLY ---
    st.write("**⚠️ Report Issue**")
    
    msg_val = st.text_input("Message to Director:", placeholder="Type issue here...", key="pool_manual_input")

    if st.button("Send Alert"):
        if msg_val:
            state.add_alert("POOL BAR", msg_val)
            state.last_update = time.time()
            st.toast("Alert Logged to System!", icon="📨")

    # Feedback Loop (Status Update for Staff)
    pool_alerts = [a for a in state.alert_log if a['source'] == "POOL BAR"]
    
    if pool_alerts:
        last_alert = pool_alerts[-1] # Παίρνουμε το τελευταίο
        if last_alert['status'] == "Pending":
            st.warning(f"⏳ **Pending:** {last_alert['msg']} (Sent: {last_alert['time']})")
        else:
            st.success(f"✅ **Acknowledged by GM:** {last_alert['msg']}")

# ==========================================
# TAB 2: RECEPTION (REVENUE ONLY)
# ==========================================
with tab2:
    st.subheader("Front Desk")
    st.caption("Check-In & Revenue Operations")
    
    if st.button("🔍 Search Booking #4052"):
        st.session_state.search_done = True
        st.session_state.sold = False 
        st.toast("Guest Found", icon="👤")

    if st.session_state.search_done:
        k1, k2 = st.columns(2)
        k1.metric("Current Rate", "100€")
        k2.metric("Suite Upgrade", "150€", delta="+50€")
        
        if st.button("✅ Confirm Upgrade (+50€)"):
            state.upsell_revenue += 50
            state.last_transaction = "Reception (Upgrade #4052)"
            state.last_update = time.time()
            st.session_state.sold = True
            st.balloons()
        
        if st.session_state.sold:
             st.success("💰 Revenue Added!")

# ==========================================
# TAB 3: GM DASHBOARD (THE BRAIN)
# ==========================================
with tab3:
    st.subheader("GM Dashboard (Command Center)")
    
    col_gm_left, col_gm_right = st.columns([1.2, 1.5]) 

    # --- LEFT: LIVE MONITORING ---
    with col_gm_left:
        st.markdown('<div class="context-label">DEPARTMENT STATUS</div>', unsafe_allow_html=True)
        
        # STATUS BARS
        if state.upsell_revenue > 0:
            st.markdown(f'<div class="status-gm">🛎️ RECEPTION: ACTIVE ({state.upsell_revenue}€)</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="status-gm">🛎️ RECEPTION: OPEN</div>', unsafe_allow_html=True)
            
        cnt = sum(state.checks.values())
        if cnt == 4:
            st.markdown(f'<div class="status-gm">🍹 POOL BAR: READY ({state.completion_time})</div>', unsafe_allow_html=True)
        elif cnt > 0:
            st.markdown(f'<div class="warn-gm">🍹 POOL BAR: SETTING UP ({cnt}/4)</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="alert-gm">🍹 POOL BAR: PENDING</div>', unsafe_allow_html=True)
            
        st.markdown('<div class="warn-gm">🧹 HOUSEKEEPING: TURNDOWN (60%)</div>', unsafe_allow_html=True)
        
        st.divider()
        
        # FINANCIAL LOG BUTTON
        st.markdown('<div class="context-label">FINANCIAL</div>', unsafe_allow_html=True)
        st.metric("Total Upsell", f"{state.upsell_revenue}€")
        if st.button("📄 View Financial Report"):
             st.toast("Opening Revenue_Log_2025.xlsx...", icon="📊")

    # --- RIGHT: INTELLIGENCE CENTER ---
    with col_gm_right:
        
        # --- 1. ALERT LOG SYSTEM (PRIORITY VIEW) ---
        st.markdown('<div class="context-label">⚠️ ACTIVE ISSUES (PRIORITY VIEW)</div>', unsafe_allow_html=True)
        
        # Βρίσκουμε ΜΟΝΟ τα Pending
        pending_alerts = [a for a in state.alert_log if a['status'] == "Pending"]
        
        if not pending_alerts:
            st.success("✅ No Active Issues")
        else:
            # Δείχνουμε τα 3 τελευταία για να μην γεμίζει η οθόνη
            for alert in pending_alerts[-3:]:
                with st.container():
                    # Κάρτα Alert
                    st.markdown(f"""
                    <div class="alert-card">
                        <b>{alert['source']}</b> ({alert['time']}): {alert['msg']}
                    </div>
                    """, unsafe_allow_html=True)
                    # Κουμπί Ack για το συγκεκριμένο Alert
                    if st.button(f"✅ Mark Solved (ID: {alert['id']})", key=f"btn_{alert['id']}"):
                        alert['status'] = "Acknowledged" # Εδώ αλλάζει το status στη βάση
                        state.last_update = time.time()
                        st.rerun()
        
        # ΤΟ ΚΟΥΜΠΙ ΓΙΑ ΤΟ ΙΣΤΟΡΙΚΟ (LOGS)
        st.write("")
        if st.button("📂 View Full Issue Log (History)"):
            st.toast("Opening Maintenance_Log.xlsx...", icon="🛠️")
            if state.alert_log:
                df = pd.DataFrame(state.alert_log)
                st.dataframe(df[['time', 'source', 'msg', 'status']].tail(10), hide_index=True)

        st.divider()

        # --- 2. AI REPUTATION SCANNER ---
        st.markdown('<div class="context-label">✨ AI REPUTATION MONITOR</div>', unsafe_allow_html=True)
        
        c_rev1, c_rev2 = st.columns([2, 1])
        with c_rev1:
            st.caption("Auto-Scan: Booking.com, TripAdvisor, Google")
        with c_rev2:
            if st.button("🔄 Sync Now"):
                state.reviews_scanned = True
                # Προσομοίωση ότι βρέθηκε κριτική
                state.latest_online_review = {
                    "source": "Booking.com",
                    "rating": 4,
                    "guest": "John D.",
                    "text": "Great hotel, but the pool music was too loud during siesta hours.",
                }
                st.toast("Sync Complete. 1 New Review Found.", icon="🌍")
        
        if state.reviews_scanned and state.latest_online_review:
            rev = state.latest_online_review
            
            # Εμφάνιση της Κριτικής
            st.markdown(f"""
            <div class="review-card">
                <b>🆕 New Review on {rev['source']}</b><br>
                Ratings: {'⭐' * rev['rating']}<br>
                <i>"{rev['text']}"</i>
            </div>
            """, unsafe_allow_html=True)
            
            # AI SUGGESTION
            st.markdown("**🤖 Athena Suggestion:**")
            st.info(f"Draft Reply: 'Dear {rev['guest']}, thank you for your feedback! We apologize for the music volume; we have already instructed the Pool Bar team to adjust it between 14:00-17:00. We hope to see you again!'")
            
            if st.button("📋 Copy Response"):
                st.toast("Response copied to clipboard!", icon="📋")

    # AUTO REFRESH LOOP
    time.sleep(2)
    st.rerun()