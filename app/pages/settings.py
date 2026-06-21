import streamlit as st

import config.config as cfg
from app.services.ai_service import ai_service
from src.services.translation_service import t

st.markdown(
    f'<h1 class="gradient-text" style="font-size: 3rem; margin-bottom: 5px;">{t("settings_page_title")}</h1>',
    unsafe_allow_html=True,
)
st.markdown(
    f"<p style='font-size: 1.1rem; font-weight: bold; color: #1040C0;'>{t('settings_subtitle')}</p>",
    unsafe_allow_html=True,
)
st.markdown("---")

col_settings, col_info = st.columns([2, 1])

with col_settings:
    st.markdown(
        f"""
        <div class="bauhaus-card card-red" style="padding: 20px;">
            <h3 style="margin-top: 0px;">{t("settings_cv_hyperparameters")}</h3>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # MediaPipe Thresholds
    mp_det_conf = st.slider(
        t("settings_mp_det_conf"),
        min_value=0.1,
        max_value=1.0,
        value=cfg.MP_MIN_DETECTION_CONFIDENCE,
        step=0.05,
        key="set_mp_min_det",
    )

    mp_track_conf = st.slider(
        t("settings_mp_track_conf"),
        min_value=0.1,
        max_value=1.0,
        value=cfg.MP_MIN_TRACKING_CONFIDENCE,
        step=0.05,
        key="set_mp_min_track",
    )

    # Classification Thresholds
    cls_conf = st.slider(
        t("settings_cls_conf"),
        min_value=0.1,
        max_value=1.0,
        value=cfg.GESTURE_CONFIDENCE_THRESHOLD,
        step=0.05,
        key="set_cls_conf",
    )

    st.markdown(f"### {t('settings_hardware_configs')}")

    cam_source = st.number_input(
        t("settings_cam_source"),
        min_value=0,
        max_value=5,
        value=cfg.WEBCAM_SOURCE,
        step=1,
        key="set_cam_source",
    )

    if st.button(
        f"💾 {t('settings_save_btn')}",
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

        st.success(t("settings_save_success"))

with col_info:
    st.markdown(
        f"""
        <div class="bauhaus-card card-blue" style="padding: 20px;">
            <h3 style="margin-top: 0px;">{t("settings_deployment_pathways")}</h3>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        f"""
        <div class="bauhaus-card" style="padding: 20px;">
            <div style="font-size:0.85rem; margin-bottom:12px;">
                <strong>{t("settings_base_dir")}:</strong><br/>
                <code style="color:#1040C0;">{cfg.BASE_DIR}</code>
            </div>
            <div style="font-size:0.85rem; margin-bottom:12px;">
                <strong>{t("settings_dataset_path")}:</strong><br/>
                <code style="color:#1040C0;">{cfg.DATASETS_DIR}</code>
            </div>
            <div style="font-size:0.85rem;">
                <strong>{t("settings_models_path")}:</strong><br/>
                <code style="color:#1040C0;">{cfg.MODELS_DIR}</code>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.info(f"ℹ️ {t('settings_info')}")
