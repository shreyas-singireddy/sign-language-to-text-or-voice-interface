import streamlit as st
import pandas as pd
from app.services.database_service import db_service

# Page Header
st.markdown('<h1 class="gradient-text" style="font-size: 3rem; margin-bottom: 5px;">ANALYTICS DASHBOARD</h1>', unsafe_allow_html=True)
st.markdown("<p style='font-size: 1.1rem; font-weight: bold; color: #1040C0;'>System usage analytics, classification confidence tracks, and translation distributions.</p>", unsafe_allow_html=True)
st.markdown("---")

analytics = db_service.get_analytics()

# Highlight Metrics Row
m_col1, m_col2, m_col3 = st.columns(3)
with m_col1:
    st.markdown(
        f"""
        <div class="bauhaus-card card-red" style="padding: 15px; text-align: center;">
            <span style="font-size: 0.85rem; font-weight: bold; color: #555555; text-transform: uppercase;">Total Translated</span>
            <h2 style="font-size: 2.8rem; margin: 5px 0 0 0;">{analytics["total_translations"]}</h2>
        </div>
        """,
        unsafe_allow_html=True
    )
with m_col2:
    st.markdown(
        f"""
        <div class="bauhaus-card card-blue" style="padding: 15px; text-align: center;">
            <span style="font-size: 0.85rem; font-weight: bold; color: #555555; text-transform: uppercase;">Avg Classifier Confidence</span>
            <h2 style="font-size: 2.8rem; margin: 5px 0 0 0;">{int(analytics['average_confidence'] * 100)}%</h2>
        </div>
        """,
        unsafe_allow_html=True
    )
with m_col3:
    db_status = analytics["db_status"]
    st.markdown(
        f"""
        <div class="bauhaus-card card-yellow" style="padding: 15px; text-align: center;">
            <span style="font-size: 0.85rem; font-weight: bold; color: #555555; text-transform: uppercase;">Database Link</span>
            <h2 style="font-size: 2.8rem; margin: 5px 0 0 0; color: {'#D02020' if db_status == 'Offline' else '#121212'} !important;">{db_status}</h2>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("---")

if analytics["total_translations"] > 0:
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.markdown("### Gesture Token Frequency")
        gesture_freq = analytics["gesture_frequency"]
        if gesture_freq:
            df_g = pd.DataFrame(list(gesture_freq.items()), columns=["Gesture", "Frequency"]).sort_values("Frequency", ascending=False)
            st.bar_chart(df_g.set_index("Gesture"))
        else:
            st.info("Insufficient gesture data.")

    with col_right:
        st.markdown("### Language Distribution")
        lang_dist = analytics["language_distribution"]
        if lang_dist:
            df_l = pd.DataFrame(list(lang_dist.items()), columns=["Language", "Translations"])
            st.bar_chart(df_l.set_index("Language"))
        else:
            st.info("Insufficient language data.")

    # Timeline view
    st.markdown("### Daily Usage Timeline")
    daily_act = analytics["daily_activity"]
    if daily_act:
        df_d = pd.DataFrame(list(daily_act.items()), columns=["Date", "Translations"]).sort_values("Date")
        st.line_chart(df_d.set_index("Date"))
    else:
        st.info("Insufficient daily history data.")
else:
    st.info("Analytics will display charts after a history of translations has been recorded. Go to 'Live Translation' page to start.")
