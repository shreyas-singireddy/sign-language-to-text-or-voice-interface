import os
import platform
import sys

import streamlit as st

from config.config import DB_NAME, MONGO_URI
from database.mongodb import db_conn

# Page Header
st.markdown(
    '<h1 class="gradient-text" style="font-size: 3rem; margin-bottom: 5px;">ADMIN DASHBOARD</h1>',
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='font-size: 1.1rem; font-weight: bold; color: #1040C0;'>System diagnostics, process configurations, and database administration tools.</p>",
    unsafe_allow_html=True,
)
st.markdown("---")

col_system, col_db = st.columns([1, 1])

with col_system:
    st.markdown(
        """
        <div class="bauhaus-card card-red" style="padding: 20px;">
            <h3 style="margin-top: 0px;">HOST ENVIRONMENT DIAGNOSTICS</h3>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Render system spec details
    st.markdown(
        f"""
        <div class="bauhaus-card" style="padding: 20px;">
            <h4 style="margin-top:0px; color:#D02020 !important;">Server Specifications</h4>
            <hr style="margin: 8px 0; border: 0; border-top: 2px solid #121212;"/>
            <table style="width:100%; font-size:0.9rem; line-height: 1.8;">
                <tr><td><strong>OS Platform:</strong></td><td>{platform.system()} {platform.release()}</td></tr>
                <tr><td><strong>Python Execution:</strong></td><td>{sys.version.split()[0]}</td></tr>
                <tr><td><strong>Streamlit version:</strong></td><td>{st.__version__}</td></tr>
                <tr><td><strong>PID:</strong></td><td>{os.getpid()}</td></tr>
            </table>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### Admin Action Logs")
    if st.button(
        "🧹 Clear Offline History Backup",
        key="btn_clear_offline_history",
        use_container_width=True,
    ):
        import json

        from app.services.database_service import OFFLINE_HISTORY_FILE

        try:
            with open(OFFLINE_HISTORY_FILE, "w") as f:
                json.dump([], f)
            st.success("Successfully cleared local offline translation log history!")
        except Exception as e:
            st.error(f"Error clearing history file: {e}")

with col_db:
    st.markdown(
        """
        <div class="bauhaus-card card-blue" style="padding: 20px;">
            <h3 style="margin-top: 0px;">DATABASE MONITORING</h3>
        </div>
        """,
        unsafe_allow_html=True,
    )

    is_connected = db_conn.is_connected()
    db_status = "ONLINE" if is_connected else "OFFLINE"
    status_class = "status-online" if is_connected else "status-offline"

    st.markdown(
        f"""
        <div class="bauhaus-card" style="padding: 20px;">
            <h4 style="margin-top:0px; display:flex; justify-content:space-between; align-items:center;">
                <span>MongoDB Atlas Link</span>
                <span class="status-pill {status_class}">{db_status}</span>
            </h4>
            <hr style="margin: 8px 0; border: 0; border-top: 2px solid #121212;"/>
            <div style="font-size:0.85rem; margin-bottom:8px;">
                <strong>Cluster Database Name:</strong><br/>
                <code>{DB_NAME}</code>
            </div>
            <div style="font-size:0.85rem;">
                <strong>Connection Endpoint:</strong><br/>
                <code style="word-break: break-all;">{MONGO_URI if MONGO_URI else "Not configured in env variables"}</code>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### Connectivity Check")
    if st.button(
        "🔌 Ping Database Cluster", key="btn_ping_db", use_container_width=True
    ):
        db_conn.close()
        success = db_conn.connect()
        if success:
            st.success("MongoDB Atlas connection established and successfully pinged!")
            st.rerun()
        else:
            st.error(
                "Failed to connect to MongoDB. Check configuration URI and network access permissions."
            )
