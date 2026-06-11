"""
SignBridge AI — Upgraded Analytics Dashboard (Layer 9)
Full Plotly analytics platform with gesture heatmaps, emotion distribution,
confidence histograms, language breakdown, and daily activity charts.
"""

import plotly.graph_objects as go
import streamlit as st

from analytics.metrics_collector import metrics_collector
from analytics.report_generator import report_generator
from app.services.database_service import db_service

# ─── Page Header ────────────────────────────────────────────────────────────────
st.markdown(
    """
    <h1 style="font-size: 3rem; margin-bottom: 5px; text-transform: uppercase; font-family: 'Space Grotesk', sans-serif; font-weight: 900;">
        ANALYTICS PLATFORM
    </h1>
    <p style='font-size: 1.1rem; font-weight: bold; color: #1040C0;'>
        Real-time translation telemetry, gesture heatmaps, confidence tracking, and language distribution.
    </p>
    """,
    unsafe_allow_html=True,
)
st.markdown("---")

# ─── Load Data ──────────────────────────────────────────────────────────────────
db_analytics = db_service.get_analytics()
report = report_generator.generate_full_report(db_analytics)
summary = report["summary"]

# ─── KPI Metric Row ─────────────────────────────────────────────────────────────
kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
with kpi_col1:
    st.markdown(
        f"""
        <div class="bauhaus-card card-red" style="padding: 15px; text-align: center;">
            <span style="font-size: 0.8rem; font-weight: 700; color: #555; text-transform: uppercase;">Total Translations</span>
            <h2 style="font-size: 2.8rem; margin: 5px 0 0 0;">{summary['total_translations']}</h2>
        </div>
        """,
        unsafe_allow_html=True,
    )
with kpi_col2:
    avg_conf_pct = int(summary["average_confidence"] * 100)
    st.markdown(
        f"""
        <div class="bauhaus-card card-blue" style="padding: 15px; text-align: center;">
            <span style="font-size: 0.8rem; font-weight: 700; color: #555; text-transform: uppercase;">Avg Confidence</span>
            <h2 style="font-size: 2.8rem; margin: 5px 0 0 0;">{avg_conf_pct}%</h2>
        </div>
        """,
        unsafe_allow_html=True,
    )
with kpi_col3:
    latency = summary.get("average_latency_ms", 0)
    st.markdown(
        f"""
        <div class="bauhaus-card card-yellow" style="padding: 15px; text-align: center;">
            <span style="font-size: 0.8rem; font-weight: 700; color: #555; text-transform: uppercase;">Avg Latency</span>
            <h2 style="font-size: 2.8rem; margin: 5px 0 0 0;">{latency:.0f}<small style="font-size: 1.2rem;">ms</small></h2>
        </div>
        """,
        unsafe_allow_html=True,
    )
with kpi_col4:
    db_status = db_analytics.get("db_status", "Unknown")
    status_color = "#D02020" if db_status == "Offline" else "#121212"
    st.markdown(
        f"""
        <div class="bauhaus-card" style="padding: 15px; text-align: center; border-top: 15px solid {'#D02020' if db_status == 'Offline' else '#208040'} !important;">
            <span style="font-size: 0.8rem; font-weight: 700; color: #555; text-transform: uppercase;">Database</span>
            <h2 style="font-size: 2.8rem; margin: 5px 0 0 0; color: {status_color} !important;">{db_status}</h2>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("---")

# ─── CHARTS GRID ────────────────────────────────────────────────────────────────
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    # Gesture Frequency Bar Chart
    gesture_data = report["gesture_bar"]
    if gesture_data["x"]:
        fig_gesture = go.Figure(
            go.Bar(
                x=gesture_data["x"],
                y=gesture_data["y"],
                marker_color="#D02020",
                marker_line_color="#121212",
                marker_line_width=2,
            )
        )
        fig_gesture.update_layout(
            title="Top Gesture Frequencies",
            xaxis_title="Gesture Token",
            yaxis_title="Count",
            plot_bgcolor="#F0F0F0",
            paper_bgcolor="#FFFFFF",
            font=dict(family="Outfit", size=12, color="#121212"),
            title_font=dict(size=16, color="#121212", family="Space Grotesk"),
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor="#E0E0E0"),
            margin=dict(l=20, r=20, t=50, b=20),
        )
        st.plotly_chart(fig_gesture, use_container_width=True)
    else:
        st.info("No gesture data yet. Start translating to generate analytics.")

with chart_col2:
    # Language Distribution Bar Chart
    lang_data = report["language_bar"]
    if lang_data["x"]:
        fig_lang = go.Figure(
            go.Bar(
                x=lang_data["x"],
                y=lang_data["y"],
                marker_color="#1040C0",
                marker_line_color="#121212",
                marker_line_width=2,
            )
        )
        fig_lang.update_layout(
            title="Translation Language Distribution",
            xaxis_title="Language",
            yaxis_title="Translations",
            plot_bgcolor="#F0F0F0",
            paper_bgcolor="#FFFFFF",
            font=dict(family="Outfit", size=12, color="#121212"),
            title_font=dict(size=16, color="#121212", family="Space Grotesk"),
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor="#E0E0E0"),
            margin=dict(l=20, r=20, t=50, b=20),
        )
        st.plotly_chart(fig_lang, use_container_width=True)
    else:
        st.info("No language data yet.")

# ─── EMOTION PIE + CONFIDENCE HISTOGRAM ─────────────────────────────────────────
st.markdown("---")
pie_col, hist_col = st.columns(2)

with pie_col:
    emotion_data = report["emotion_pie"]
    if emotion_data["values"] and any(v > 0 for v in emotion_data["values"]):
        fig_emotion = go.Figure(
            go.Pie(
                labels=emotion_data["labels"],
                values=emotion_data["values"],
                marker=dict(
                    colors=emotion_data["colors"], line=dict(color="#121212", width=2)
                ),
                hole=0.4,
                textfont=dict(family="Outfit", size=13, color="#FFFFFF"),
            )
        )
        fig_emotion.update_layout(
            title="Emotion Tone Distribution",
            paper_bgcolor="#FFFFFF",
            font=dict(family="Outfit", size=12, color="#121212"),
            title_font=dict(size=16, color="#121212", family="Space Grotesk"),
            legend=dict(font=dict(family="Outfit")),
            margin=dict(l=20, r=20, t=50, b=20),
        )
        st.plotly_chart(fig_emotion, use_container_width=True)
    else:
        st.info("Emotion data will appear after translations are processed.")

with hist_col:
    conf_data = report["confidence_bars"]
    if conf_data["buckets"]:
        fig_conf = go.Figure(
            go.Bar(
                x=conf_data["buckets"],
                y=conf_data["counts"],
                marker_color="#F0C020",
                marker_line_color="#121212",
                marker_line_width=2,
            )
        )
        fig_conf.update_layout(
            title="Confidence Score Distribution",
            xaxis_title="Confidence Range",
            yaxis_title="Frequency",
            plot_bgcolor="#F0F0F0",
            paper_bgcolor="#FFFFFF",
            font=dict(family="Outfit", size=12, color="#121212"),
            title_font=dict(size=16, color="#121212", family="Space Grotesk"),
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor="#E0E0E0"),
            margin=dict(l=20, r=20, t=50, b=20),
        )
        st.plotly_chart(fig_conf, use_container_width=True)
    else:
        st.info("Confidence histogram data will appear after translations.")

# ─── DAILY ACTIVITY TIMELINE ─────────────────────────────────────────────────────
st.markdown("---")
daily_data = report["daily_line"]
if daily_data["x"]:
    fig_daily = go.Figure(
        go.Scatter(
            x=daily_data["x"],
            y=daily_data["y"],
            mode="lines+markers",
            line=dict(color="#121212", width=3),
            marker=dict(color="#D02020", size=10, line=dict(color="#121212", width=2)),
            fill="tozeroy",
            fillcolor="rgba(208, 32, 32, 0.1)",
        )
    )
    fig_daily.update_layout(
        title="Daily Translation Activity",
        xaxis_title="Date",
        yaxis_title="Translations",
        plot_bgcolor="#F0F0F0",
        paper_bgcolor="#FFFFFF",
        font=dict(family="Outfit", size=12, color="#121212"),
        title_font=dict(size=18, color="#121212", family="Space Grotesk"),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor="#E0E0E0"),
        margin=dict(l=20, r=20, t=60, b=20),
    )
    st.plotly_chart(fig_daily, use_container_width=True)
else:
    st.info("Daily activity chart will appear after translation sessions are recorded.")

# ─── METRICS RESET CONTROL ───────────────────────────────────────────────────────
st.markdown("---")
if st.button(
    "🔄 Reset Live Session Metrics", key="btn_reset_metrics", use_container_width=True
):
    metrics_collector.reset()
    st.success("Live session metrics reset.")
    st.rerun()
