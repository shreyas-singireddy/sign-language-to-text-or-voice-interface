import time

import streamlit as st

from app.services.ai_service import ai_service
from config.config import SUPPORTED_GESTURES
from src.services.translation_service import t

# Page Header
st.markdown(
    f'<h1 class="gradient-text" style="font-size: 3rem; margin-bottom: 5px;">{t("training_title")}</h1>',
    unsafe_allow_html=True,
)
st.markdown(
    f"<p style='font-size: 1.1rem; font-weight: bold; color: #1040C0;'>{t('ts_subtitle')}</p>",
    unsafe_allow_html=True,
)
st.markdown("---")

col_control, col_dataset = st.columns([1, 1])

with col_control:
    st.markdown(
        f"""
        <div class="bauhaus-card card-red" style="padding: 20px;">
            <h3 style="margin-top: 0px;">{t("ts_record_landmark")}</h3>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Form input for label
    selected_label = st.selectbox(t("ts_target_label"), options=SUPPORTED_GESTURES, key="select_training_label")

    custom_label = st.text_input(t("ts_define_custom"), value="", key="input_custom_label")
    label_to_record = custom_label.strip().upper() if custom_label.strip() else selected_label

    frames_to_record = st.slider(
        t("ts_seq_len"),
        min_value=10,
        max_value=60,
        value=30,
        step=5,
    )

    # Capture control buttons
    st.markdown(t("ts_before_recording"))

    record_button = st.button(
        f"🔴 {t('ts_start_recording')}",
        key="btn_start_record_sample",
        use_container_width=True,
    )

    if record_button:
        status_box = st.empty()
        progress_bar = st.progress(0.0)

        # Open camera manager
        from ai_engine.computer_vision.camera import CameraManager

        cam = CameraManager()
        if cam.start():
            try:
                status_box.warning("Get Ready... 3")
                time.sleep(1)
                status_box.warning("Get Ready... 2")
                time.sleep(1)
                status_box.warning("Get Ready... 1")
                time.sleep(1)

                status_box.error(f"RECORDING NOW - Perform gesture '{label_to_record}'")

                recorded_frames = 0
                sample_landmarks_seq = []

                while recorded_frames < frames_to_record:
                    success, frame = cam.get_frame()
                    if not success:
                        st.error(t("ts_capture_failed"))
                        break

                    # Process frame to extract landmarks (we don't need to draw on screen here)
                    results = ai_service.pipeline.holistic_manager.process_frame(frame)
                    landmarks = ai_service.pipeline.extractor.extract_landmarks(results)

                    sample_landmarks_seq.append(landmarks.tolist())

                    recorded_frames += 1
                    progress_bar.progress(recorded_frames / frames_to_record)
                    time.sleep(0.05)  # ~20 FPS capture rate

                # Save sequence
                success = ai_service.record_sample(label_to_record, sample_landmarks_seq)
                if success:
                    status_box.success(
                        t("ts_record_success", frames=frames_to_record, label=label_to_record)
                    )
                else:
                    status_box.error(t("ts_save_failed"))
            finally:
                cam.stop()
        else:
            st.error(t("ts_camera_error"))

with col_dataset:
    st.markdown(
        f"""
        <div class="bauhaus-card card-blue" style="padding: 20px;">
            <h3 style="margin-top: 0px;">{t("ts_dataset_inventory")}</h3>
        </div>
        """,
        unsafe_allow_html=True,
    )

    stats = ai_service.get_dataset_stats()

    if stats:
        # Render a clean table of recorded samples
        import pandas as pd

        df = pd.DataFrame(list(stats.items()), columns=["Gesture Label", "Recorded Repetitions"])
        st.dataframe(df, use_container_width=True, hide_index=True)

        # Clear specific label dataset
        st.markdown(f"### {t('ts_manage_dataset')}")
        label_to_clear = st.selectbox(
            t("ts_select_delete_label"),
            options=list(stats.keys()),
            key="select_clear_label",
        )

        if st.button(
            f"🗑️ {t('ts_delete_label')}",
            key="btn_clear_label",
            use_container_width=True,
        ):
            if (
                ai_service.clear_label_dataset(label_to_clear)
                if hasattr(ai_service, "clear_label_dataset")
                else ai_service.clear_dataset_label(label_to_clear)
            ):
                st.success(t("ts_clear_success", label=label_to_clear))
                st.rerun()
            else:
                st.error(t("ts_clear_failed"))
    else:
        st.info(t("ts_no_datasets"))
