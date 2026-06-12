import streamlit as st

import config.config as cfg
from app.services.ai_service import ai_service

# Page Header
st.markdown(
    '<h1 class="gradient-text" style="font-size: 3rem; margin-bottom: 5px;">CONFIGURATION SETTINGS</h1>',
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='font-size: 1.1rem; font-weight: bold; color: #1040C0;'>Fine-tune computer vision parameters, detection thresholds, and system preferences.</p>",
    unsafe_allow_html=True,
)
st.markdown("---")

col_settings, col_info = st.columns([2, 1])

with col_settings:
    st.markdown(
        """
        <div class="bauhaus-card card-red" style="padding: 20px;">
            <h3 style="margin-top: 0px;">COMPUTER VISION HYPERPARAMETERS</h3>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # MediaPipe Thresholds
    mp_det_conf = st.slider(
        "MediaPipe Minimum Detection Confidence",
        min_value=0.1,
        max_value=1.0,
        value=cfg.MP_MIN_DETECTION_CONFIDENCE,
        step=0.05,
        key="set_mp_min_det",
    )

    mp_track_conf = st.slider(
        "MediaPipe Minimum Tracking Confidence",
        min_value=0.1,
        max_value=1.0,
        value=cfg.MP_MIN_TRACKING_CONFIDENCE,
        step=0.05,
        key="set_mp_min_track",
    )

    # Classification Thresholds
    cls_conf = st.slider(
        "Gesture Classifier Confidence Threshold",
        min_value=0.1,
        max_value=1.0,
        value=cfg.GESTURE_CONFIDENCE_THRESHOLD,
        step=0.05,
        key="set_cls_conf",
    )

    st.markdown("### Hardware Configurations")

    cam_source = st.number_input(
        "Webcam Input Source index",
        min_value=0,
        max_value=5,
        value=cfg.WEBCAM_SOURCE,
        step=1,
        key="set_cam_source",
    )

    # Save button
    if st.button(
        "💾 Apply Configuration Settings",
        key="btn_save_settings",
        use_container_width=True,
    ):
        # Apply configurations to global state
        cfg.MP_MIN_DETECTION_CONFIDENCE = mp_det_conf
        cfg.MP_MIN_TRACKING_CONFIDENCE = mp_track_conf
        cfg.GESTURE_CONFIDENCE_THRESHOLD = cls_conf
        cfg.WEBCAM_SOURCE = int(cam_source)

        # Force reinitialization of models with new parameters
        ai_service.pipeline.holistic_manager._initialized = False
        ai_service.pipeline.holistic_manager.initialize()

        st.success("Configuration settings updated successfully and pipeline reinitialized!")

with col_info:
    st.markdown(
        """
        <div class="bauhaus-card card-blue" style="padding: 20px;">
            <h3 style="margin-top: 0px;">DEPLOYMENT PATHWAYS</h3>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        f"""
        <div class="bauhaus-card" style="padding: 20px;">
            <div style="font-size:0.85rem; margin-bottom:12px;">
                <strong>Base Directory:</strong><br/>
                <code style="color:#1040C0;">{cfg.BASE_DIR}</code>
            </div>
            <div style="font-size:0.85rem; margin-bottom:12px;">
                <strong>Dataset Storage Path:</strong><br/>
                <code style="color:#1040C0;">{cfg.DATASETS_DIR}</code>
            </div>
            <div style="font-size:0.85rem;">
                <strong>Models Assets Path:</strong><br/>
                <code style="color:#1040C0;">{cfg.MODELS_DIR}</code>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.info(
        "ℹ️ Information: MediaPipe parameters determine the strictness of facial and hand bone skeleton estimation. If skeletons flicker, reduce the threshold levels."
    )
