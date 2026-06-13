import time

import streamlit as st

from ai_engine.utils.dependency_guard import CV2_AVAILABLE, cv2, require_torch
from src.services.translation_service import t

# --- Graceful degradation gate ---
if not CV2_AVAILABLE:
    st.warning(
        "⚠️ **Live Gesture Recognition is unavailable in this deployment.**\n\n"
        "This page requires OpenCV which could not be loaded. "
        "All other pages remain fully functional.",
        icon="🚫",
    )
    st.stop()

if not require_torch():
    st.stop()

import pandas as pd

from ai_engine.ai_agent.error_detection import error_detector
from database.learning_schemas import learning_db

# Graceful Plotly import with fallback check
try:
    import plotly.graph_objects as go
except ImportError:
    go = None

from ai_engine.gesture_recognition.services.gesture_service import gesture_service
from ai_engine.services.perception_service import perception_service
from ai_engine.utils.config import sys_config

# Page headers
st.markdown(
    f'<h1 class="gradient-text" style="font-size: 3.5rem; margin-bottom: 5px; letter-spacing: -2px;">{t("lgr_title")}</h1>',
    unsafe_allow_html=True,
)
st.markdown(
    f"<p style='font-size: 1.25rem; font-weight: 700; color: #1040C0; text-transform: uppercase;'>{t('lgr_subtitle')}</p>",
    unsafe_allow_html=True,
)
st.markdown("---")

# Session state trackers
if "gesture_cam_active" not in st.session_state:
    st.session_state["gesture_cam_active"] = False
if "custom_rec_active" not in st.session_state:
    st.session_state["custom_rec_active"] = False
if "rec_frame_count" not in st.session_state:
    st.session_state["rec_frame_count"] = 0
if "predictions_log" not in st.session_state:
    st.session_state["predictions_log"] = []
if "gesture_sentence" not in st.session_state:
    st.session_state["gesture_sentence"] = ""
if "sequence_buffer" not in st.session_state:
    st.session_state["sequence_buffer"] = []

# Charts data buffers
if "chart_latency" not in st.session_state:
    st.session_state["chart_latency"] = []
if "chart_confidence" not in st.session_state:
    st.session_state["chart_confidence"] = []

# Main layout grid
col_cam, col_panels = st.columns([1, 1])

# Empty structures to populate
prediction_data = {"prediction": "IDLE", "confidence": 0.0, "alternatives": []}
telemetry_data = None

with col_cam:
    st.markdown(
        f"""
        <div class="bauhaus-card card-red" style="padding: 15px; margin-bottom: 15px;">
            <h3 style="margin: 0; font-size: 1.4rem;">🎥 {t("lgr_gesture_stream")}</h3>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Model configuration selector
    st.markdown(f"### {t('lgr_inference_settings')}")
    model_mode = st.selectbox(
        t("lgr_inference_model_type"),
        ["Alphabet (Static A-Z/0-9)", "Word Model (Temporal Sequences)"],
        format_func=lambda x: t("lgr_alphabet_mode") if x.startswith("Alphabet") else t("lgr_word_mode"),
        key="select_model_mode",
    )

    selected_arch = st.selectbox(
        t("lgr_seq_arch_model"),
        ["LSTM", "BiLSTM", "Transformer", "TCN"],
        index=0,
        key="select_seq_arch",
    )

    # Controls
    ctrl_col1, ctrl_col2, ctrl_col3 = st.columns(3)
    with ctrl_col1:
        if st.button(t("lgr_start_predictor"), key="btn_start_gest_cam"):
            st.session_state["gesture_cam_active"] = True
            st.session_state["predictions_log"].clear()
            st.session_state["sequence_buffer"].clear()
            st.session_state["gesture_sentence"] = ""
    with ctrl_col2:
        if st.button(t("lgr_stop_predictor"), key="btn_stop_gest_cam"):
            st.session_state["gesture_cam_active"] = False
    with ctrl_col3:
        if st.button(t("lgr_reset_timeline"), key="btn_clear_gest_seq"):
            st.session_state["predictions_log"].clear()
            st.session_state["sequence_buffer"].clear()
            st.session_state["gesture_sentence"] = ""
            st.success(t("lgr_buffer_cleared"))

    video_view = st.empty()

    if st.session_state["gesture_cam_active"]:
        st.markdown(
            f'<div class="pulse-badge">● {t("lgr_active_broadcast")}</div>',
            unsafe_allow_html=True,
        )

        # Start camera manager
        success = perception_service.camera.initialize_camera(sys_config.camera.source_index)
        if success:
            try:
                while st.session_state["gesture_cam_active"]:
                    read_success, frame, latency = perception_service.camera.read_frame()
                    if not read_success:
                        st.error(t("lgr_ingest_failed"))
                        break

                    # Run Perception Pipeline
                    telemetry_data = perception_service.process_perception_frame(frame, latency)
                    flat_lms = perception_service._flatten_landmarks(telemetry_data.landmarks)

                    # Compute indicators
                    readiness = telemetry_data.readiness.gesture_readiness
                    visibility = telemetry_data.visibility.overall_visibility
                    quality = telemetry_data.readiness.frame_quality_score
                    occlusion = telemetry_data.occlusion.occlusion_percentage
                    stability = telemetry_data.stability.tracking_stability

                    # Handle Recording for Training Studio
                    if st.session_state["custom_rec_active"]:
                        is_rec = gesture_service.record_frame(flat_lms, quality, visibility)
                        if is_rec:
                            st.session_state["rec_frame_count"] += 1
                            if st.session_state["rec_frame_count"] >= 30:
                                # Stop recording automatically
                                st.session_state["custom_rec_active"] = False
                                saved_path = gesture_service.stop_and_save_recording()
                                if saved_path:
                                    st.success(t("lgr_record_success").format(path=saved_path.name))
                                else:
                                    st.error(t("lgr_record_failed"))

                    # Run Gesture recognition engine
                    if model_mode.startswith("Alphabet"):
                        prediction_data = gesture_service.predict_frame(
                            flat_lms, visibility, quality, occlusion, stability
                        )
                    else:
                        st.session_state["sequence_buffer"].append(flat_lms)
                        if len(st.session_state["sequence_buffer"]) > 30:
                            st.session_state["sequence_buffer"].pop(0)

                        prediction_data = gesture_service.predict_sequence(
                            st.session_state["sequence_buffer"],
                            visibility,
                            quality,
                            occlusion,
                            stability,
                        )

                    # Log prediction history
                    pred_label = prediction_data["prediction"]
                    pred_conf = prediction_data["confidence"]

                    # Run Error Detection and log practice metrics
                    if pred_label and pred_label not in ["IDLE", "WAITING_FOR_CLEAR_GESTURE", ""]:
                        err_feedback = error_detector.detect_errors(telemetry_data.landmarks, pred_label)
                        st.session_state["latest_error_feedback"] = err_feedback
                        user_phone = st.session_state.get("user_phone", "demo_user")
                        learning_db.log_practice(user_phone, pred_conf, pred_label)

                    if pred_label not in ["IDLE", "WAITING_FOR_CLEAR_GESTURE", ""]:
                        # Append to history logs
                        if (
                            not st.session_state["predictions_log"]
                            or st.session_state["predictions_log"][-1]["prediction"] != pred_label
                        ):
                            st.session_state["predictions_log"].append(
                                {
                                    "prediction": pred_label,
                                    "timestamp": time.strftime("%H:%M:%S"),
                                    "confidence": pred_conf,
                                }
                            )
                            # Limit history size
                            if len(st.session_state["predictions_log"]) > 10:
                                st.session_state["predictions_log"].pop(0)

                            # Reconstruct phrase
                            st.session_state["gesture_sentence"] = " ".join(
                                [item["prediction"] for item in st.session_state["predictions_log"]]
                            )

                    # Mirror and render frame
                    display_img = cv2.flip(frame, 1)
                    if telemetry_data.landmarks.pose.present:
                        display_img = perception_service.pose_det.mp_pose.solutions.drawing_utils.draw_landmarks(
                            display_img, telemetry_data.landmarks.pose.landmarks, None
                        )
                    display_rgb = cv2.cvtColor(display_img, cv2.COLOR_BGR2RGB)
                    video_view.image(display_rgb, use_column_width=True)

                    # Log performance values
                    st.session_state["chart_latency"].append(telemetry_data.performance.total_pipeline_ms)
                    st.session_state["chart_confidence"].append(pred_conf * 100.0)

                    # Cap chart buffers
                    if len(st.session_state["chart_latency"]) > 50:
                        st.session_state["chart_latency"].pop(0)
                    if len(st.session_state["chart_confidence"]) > 50:
                        st.session_state["chart_confidence"].pop(0)

                    time.sleep(0.033)
            finally:
                perception_service.camera.release()
                video_view.empty()
        else:
            st.error(t("lgr_capture_device_failed"))
    else:
        video_view.info(t("lgr_camera_info"))

# ----------------- RIGHT COLUMN: CONTROL PANELS & STUDIO -----------------
with col_panels:
    tab_recognition, tab_training, tab_registry = st.tabs(
        [f"🤟 {t('lgr_tab_predictions')}", f"🏋️ {t('lgr_tab_training')}", f"🛡️ {t('lgr_tab_registry')}"]
    )

    with tab_recognition:
        # Display classification results
        curr_pred = prediction_data["prediction"]
        curr_conf = prediction_data["confidence"]

        st.markdown(
            f"""
            <div class="bauhaus-card card-blue" style="padding:20px; margin-bottom:15px; text-align: center;">
                <h4 style="margin:0 0 5px 0; font-size:1.1rem; color:#D02020 !important;">{t("lgr_active_gesture")}</h4>
                <h1 style="font-size:3.5rem; letter-spacing: -2px; margin: 5px 0;">{curr_pred}</h1>
                <div style="background-color:#E6E6E6; height:20px; border:2px solid #121212; position:relative; margin-top:10px;">
                    <div style="background-color:#F0C020; height:100%; width:{int(curr_conf * 100)}%; border-right:2px solid #121212;"></div>
                </div>
                <div style="display:flex; justify-content:space-between; margin-top:5px; font-weight:bold; font-size:0.85rem;">
                    <span>{t("lgr_confidence")}</span><span>{int(curr_conf * 100)}%</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Alternatives
        alts = prediction_data.get("alternatives", [])
        alt_str = ", ".join(alts) if alts else "None"
        st.markdown(f"**{t('lgr_top_alternatives')}** `{alt_str}`")

        # AI Postural Error Correction & Explanation
        latest_feedback = st.session_state.get("latest_error_feedback")
        if latest_feedback and latest_feedback.get("deviations"):
            st.markdown("### ⚠️ AI Alignment Feedback")
            for dev in latest_feedback["deviations"]:
                st.write(f"- **{dev['joint']}**: Variance {dev['variance']}° (Expected {dev['expected']}°, Actual {dev['actual']}°)")
            if latest_feedback.get("corrections"):
                st.info("💡 Suggestions: " + " ".join(latest_feedback["corrections"]))
        elif latest_feedback:
            st.success("✅ Perfect alignment detected!")

        # AI Sign Explainer
        if curr_pred and curr_pred not in ["IDLE", "WAITING_FOR_CLEAR_GESTURE", ""]:
            with st.expander("💡 AI Sign Explanation & Details", expanded=False):
                if st.button("Generate AI Explanation", key="btn_explain_sign_lgr"):
                    with st.spinner("Analyzing sign with AI..."):
                        from ai_engine.ai_agent.llm_engine import llm_engine
                        user_lang = st.session_state.get("language", "English")
                        prompt = (
                            f"Explain the detected sign '{curr_pred}'. "
                            f"The model detected it with a confidence score of {curr_conf * 100}%. "
                            f"Format your response in the language '{user_lang}'. "
                            "Highlight its meaning, typical context, potential misclassifications with similar signs, "
                            "and concrete suggestions to make the sign more clearly."
                        )
                        system_prompt = "You are an expert Sign Language Explainer and Accessibility Assistant."
                        explanation = llm_engine.generate_completion(prompt, system_prompt=system_prompt)
                        st.markdown(explanation)

        # Sentence output
        phrase = st.session_state["gesture_sentence"]
        st.markdown(f"### {t('lgr_decoded_output')}")
        st.markdown(
            f"""
            <div class="bauhaus-card card-yellow" style="min-height: 80px; background-color: #FFFFFF !important;">
                <p style="font-size: 1.35rem; font-weight: 800; text-transform: uppercase; margin: 0; color: #121212;">
                    {phrase if phrase else t("lgr_waiting")}
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # History log table
        st.markdown(f"### {t('lgr_recent_timeline')}")
        if st.session_state["predictions_log"]:
            df_hist = pd.DataFrame(st.session_state["predictions_log"])
            df_display = df_hist.rename(
                columns={
                    "prediction": t("lgr_col_prediction"),
                    "timestamp": t("lgr_col_timestamp"),
                    "confidence": t("lgr_col_confidence"),
                }
            )
            st.dataframe(df_display, use_container_width=True, hide_index=True)
        else:
            st.write(f"*{t('lgr_no_gestures')}*")

    with tab_training:
        st.markdown(f"### {t('lgr_create_custom')}")
        custom_label = st.text_input(t("lgr_enter_name"), value="GREETING", key="input_custom_train_label")

        # Recording controller
        st.markdown(f"#### {t('lgr_record_dataset')}")
        st.markdown(t("lgr_before_recording"))

        if st.button(
            t("lgr_start_custom_recording"),
            key="btn_start_custom_rec",
            disabled=st.session_state["custom_rec_active"],
        ):
            st.session_state["custom_rec_active"] = True
            st.session_state["rec_frame_count"] = 0

            # Start recorder session
            gesture_service.start_recording(custom_label)
            st.info(t("lgr_countdown_starting"))

        # Training panel trigger
        st.markdown("---")
        st.markdown(f"#### {t('lgr_compile_train')}")
        st.markdown(t("lgr_train_info"))

        train_epochs = st.slider(t("lgr_epochs_count"), min_value=5, max_value=50, value=15, step=5)
        train_batch = st.select_slider(t("lgr_batch_size"), options=[8, 16, 32], value=16)
        train_lr = st.selectbox(t("lgr_learning_rate"), [0.01, 0.001, 0.0001], index=1)

        if st.button(
            t("lgr_run_training"),
            key="btn_trigger_pytorch_train",
            use_container_width=True,
        ):
            with st.spinner(t("lgr_training_spinner")):
                version, metrics = gesture_service.train_gesture_model(
                    model_type="word",
                    arch_name=selected_arch,
                    epochs=train_epochs,
                    batch_size=train_batch,
                    lr=train_lr,
                )
                st.success(t("lgr_train_success").format(version=version))
                st.markdown(
                    f"""
                    <div style="background-color:#FFFFFF; border:3px solid #121212; padding:15px; color:#121212 !important;">
                        <strong>{t('lgr_test_accuracy')}</strong> {round(metrics['accuracy'] * 100, 2)}%<br/>
                        <strong>{t('lgr_macro_f1')}</strong> {round(metrics['f1_score'] * 100, 2)}%
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        # Dataset Inventory stats
        st.markdown("---")
        st.markdown(f"#### {t('lgr_dataset_inventory')}")
        stats = gesture_service.get_dataset_stats()
        if stats:
            df_stats = pd.DataFrame(list(stats.items()), columns=[t("lgr_col_label"), t("lgr_col_repetitions")])
            st.dataframe(df_stats, use_container_width=True, hide_index=True)

            label_to_delete = st.selectbox(
                t("lgr_select_clear_label"),
                options=list(stats.keys()),
                key="select_delete_label",
            )
            if st.button(t("lgr_delete_samples"), key="btn_delete_samples_label"):
                if gesture_service.clear_dataset_label(label_to_delete):
                    st.success(t("lgr_deleted_label").format(label=label_to_delete))
                    st.rerun()
        else:
            st.write(f"*{t('lgr_no_datasets')}*")

    with tab_registry:
        st.markdown(f"### {t('lgr_active_models')}")
        reg_status = gesture_service.get_registry_status()

        active_alphabet = reg_status["active_alphabet"]
        active_word = reg_status["active_word"]

        st.markdown(f"**{t('lgr_alphabet_model')}**")
        if active_alphabet:
            st.write(
                "- " + t("lgr_version_accuracy").format(version=active_alphabet['version'], acc=round(active_alphabet['metrics']['test_accuracy'] * 100, 2))
            )
        else:
            st.write(t("lgr_fallback_alphabet"))

        st.markdown(f"**{t('lgr_seq_word_model')}**")
        if active_word:
            st.write(
                "- " + t("lgr_version_accuracy").format(version=active_word['version'], acc=round(active_word['metrics']['test_accuracy'] * 100, 2))
            )
        else:
            st.write(t("lgr_fallback_word").format(arch=selected_arch))

        # Rollback utility
        st.markdown("---")
        st.markdown(f"#### {t('lgr_rollback_manager')}")
        all_models = reg_status["all_models"]

        if all_models:
            model_options = [m["version"] for m in all_models]
            rollback_target = st.selectbox(
                t("lgr_select_rollback"),
                options=model_options,
                key="select_rollback_target",
            )

            # Find selected model metadata
            selected_meta = next(m for m in all_models if m["version"] == rollback_target)
            st.write(
                "- " + t("lgr_rollback_info").format(type=selected_meta['model_type'], acc=round(selected_meta['metrics']['test_accuracy'] * 100, 2))
            )

            if st.button(
                t("lgr_rollback_btn"),
                key="btn_rollback_model",
                use_container_width=True,
            ):
                success = gesture_service.rollback_model(selected_meta["model_type"], rollback_target)
                if success:
                    st.success(t("lgr_rollback_success").format(version=rollback_target))
                    st.rerun()
                else:
                    st.error(t("lgr_rollback_failed"))
        else:
            st.write(f"*{t('lgr_no_previous_models')}*")

# ----------------- PANEL 6: REAL-TIME PLOTLY CHARTS -----------------
st.markdown("---")
st.markdown(f"### {t('lgr_performance_plots')}")

if st.session_state["chart_latency"] and go is not None:
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        fig_lat = go.Figure()
        fig_lat.add_trace(
            go.Scatter(
                y=st.session_state["chart_latency"],
                mode="lines",
                name="Pipeline Latency",
                line=dict(color="#D02020", width=3),
            )
        )
        fig_lat.update_layout(
            title=t("lgr_latency_chart"),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=20, r=20, t=40, b=20),
            height=240,
        )
        st.plotly_chart(fig_lat, use_container_width=True)

    with chart_col2:
        fig_conf = go.Figure()
        fig_conf.add_trace(
            go.Scatter(
                y=st.session_state["chart_confidence"],
                mode="lines",
                name="Confidence",
                line=dict(color="#1040C0", width=3),
            )
        )
        fig_conf.update_layout(
            title=t("lgr_confidence_chart"),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=20, r=20, t=40, b=20),
            height=240,
        )
        st.plotly_chart(fig_conf, use_container_width=True)
elif st.session_state["chart_latency"]:
    st.line_chart(
        pd.DataFrame(
            {
                t("lgr_latency_chart"): st.session_state["chart_latency"],
                t("lgr_confidence_chart"): st.session_state["chart_confidence"],
            }
        )
    )
else:
    st.info(t("lgr_no_plots"))
