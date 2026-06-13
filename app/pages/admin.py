import os
import platform
import sys

import streamlit as st

from config.config import DB_NAME, MONGO_URI
from database.mongodb import db_conn
from src.services.translation_service import t

# Page Header
st.markdown(
    f'<h1 class="gradient-text" style="font-size: 3rem; margin-bottom: 5px;">{t("admin_dashboard_title")}</h1>',
    unsafe_allow_html=True,
)
st.markdown(
    f"<p style='font-size: 1.1rem; font-weight: bold; color: #1040C0;'>{t('admin_subtitle')}</p>",
    unsafe_allow_html=True,
)
st.markdown("---")

col_system, col_db = st.columns([1, 1])

with col_system:
    st.markdown(
        f"""
        <div class="bauhaus-card card-red" style="padding: 20px;">
            <h3 style="margin-top: 0px;">{t("admin_host_diagnostics")}</h3>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Render system spec details
    st.markdown(
        f"""
        <div class="bauhaus-card" style="padding: 20px;">
            <h4 style="margin-top:0px; color:#D02020 !important;">{t("admin_server_specs")}</h4>
            <hr style="margin: 8px 0; border: 0; border-top: 2px solid #121212;"/>
            <table style="width:100%; font-size:0.9rem; line-height: 1.8;">
                <tr><td><strong>{t("admin_os_platform")}:</strong></td><td>{platform.system()} {platform.release()}</td></tr>
                <tr><td><strong>{t("admin_python_exec")}:</strong></td><td>{sys.version.split()[0]}</td></tr>
                <tr><td><strong>{t("admin_streamlit_ver")}:</strong></td><td>{st.__version__}</td></tr>
                <tr><td><strong>{t("admin_pid")}:</strong></td><td>{os.getpid()}</td></tr>
            </table>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(f"### {t('admin_action_logs')}")
    if st.button(
        f"🧹 {t('admin_clear_offline')}",
        key="btn_clear_offline_history",
        use_container_width=True,
    ):
        import json

        from app.services.database_service import OFFLINE_HISTORY_FILE

        try:
            with open(OFFLINE_HISTORY_FILE, "w") as f:
                json.dump([], f)
            st.success(t("admin_clear_success"))
        except Exception as e:
            st.error(t("admin_clear_error", error=str(e)))

with col_db:
    st.markdown(
        f"""
        <div class="bauhaus-card card-blue" style="padding: 20px;">
            <h3 style="margin-top: 0px;">{t("admin_db_monitoring")}</h3>
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
                <span>{t("admin_db_link")}</span>
                <span class="status-pill {status_class}">{db_status}</span>
            </h4>
            <hr style="margin: 8px 0; border: 0; border-top: 2px solid #121212;"/>
            <div style="font-size:0.85rem; margin-bottom:8px;">
                <strong>{t("admin_cluster_name")}:</strong><br/>
                <code>{DB_NAME}</code>
            </div>
            <div style="font-size:0.85rem;">
                <strong>{t("admin_conn_endpoint")}:</strong><br/>
                <code style="word-break: break-all;">{MONGO_URI if MONGO_URI else "Not configured in env variables"}</code>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(f"### {t('admin_conn_check')}")
    if st.button(f"🔌 {t('admin_ping_db')}", key="btn_ping_db", use_container_width=True):
        db_conn.close()
        success = db_conn.connect()
        if success:
            st.success(t("admin_ping_success"))
            st.rerun()
        else:
            st.error(t("admin_ping_failure"))
