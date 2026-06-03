# streamlit_app.py
import streamlit as st
from core.tools.mongodb_tools import MongoDBTools
from datetime import datetime

st.set_page_config(page_title="HVAC OpsForge Agent", page_icon="🔧", layout="wide")

st.title("🔧 HVAC OpsForge Agent")
st.caption("Gemini + MongoDB Powered Operations Co-Pilot for Small Trades Businesses")

# Sidebar
with st.sidebar:
    st.header("Controls")
    if st.button("Run Daily Operations Briefing", type="primary"):
        st.session_state.run_briefing = True
    st.divider()
    st.caption("Data source: MongoDB Atlas (live) + synthetic fallbacks")

# Main content
st.subheader("📊 Live Operations Snapshot")

tools = MongoDBTools()
tools.connect()

col1, col2, col3 = st.columns(3)
col1.metric("Upcoming Jobs (14d)", len(tools.get_upcoming_jobs(14)))
col2.metric("Low Stock Items", len(tools.get_low_inventory(1.2)))
col3.metric("Overdue Invoices", len(tools.get_overdue_invoices(30)))

st.divider()

st.subheader("🤖 Agent Analysis")

if st.button("Run Agent Briefing", type="primary"):
    # Simple agent-like response using the tools we have
    upcoming = tools.get_upcoming_jobs(14)
    low_stock = tools.get_low_inventory(1.2)
    overdue = tools.get_overdue_invoices(30)
    
    st.success("Agent analysis complete.")
    
    st.markdown("**Data Summary**")
    st.json({
        "upcoming_jobs": len(upcoming),
        "low_inventory_items": len(low_stock),
        "overdue_invoices": len(overdue)
    })
    
    # Proposed actions (this is where the real agent would reason)
    proposed_actions = []
    if low_stock:
        proposed_actions.append({
            "action": "inventory_reorder",
            "description": f"Reorder recommended for {len(low_stock)} parts",
            "priority": "high"
        })
    if overdue:
        proposed_actions.append({
            "action": "ar_followup",
            "description": f"Follow up on {len(overdue)} overdue invoices",
            "priority": "medium"
        })
    
    if proposed_actions:
        st.markdown("**Proposed Actions**")
        for i, action in enumerate(proposed_actions):
            st.write(f"{i+1}. **{action['action']}** — {action['description']} (Priority: {action['priority']})")
    else:
        st.info("No immediate actions required based on current data.")

st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')} | Hackathon MongoDB Track")