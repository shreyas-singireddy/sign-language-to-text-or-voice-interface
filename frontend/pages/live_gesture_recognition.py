import streamlit as st
import cv2
import numpy as np
import time
import pandas as pd
from pathlib import Path

# Graceful Plotly import with fallback check
try:
    import plotly.graph_objects as go
except ImportError:
    go = None

from ai_engine.services.perception_service import perception_service
from ai_engine.gesture_recognition.services.gesture_service import gesture_service
from ai_engine.utils.config import sys_config
from config.config import SUPPORTED_GESTURES

# Page headers
st.markdown('<h1 class="gradient-text" style="font-size: 3.5rem; margin-bottom: 5px; letter-spacing: -2px;">GESTURE CONTROL COCKPIT</h1>', unsafe_allow_html=True)
st.markdown("<p style='font-size: 1.25rem; font-weight: 700; color: #1040C0; text-transform: uppercase;'>SignBridge Real-time AI Classification & Sequence Decoding</p>", unsafe_allow_html=True)
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
        """
        <div class="bauhaus-card card-red" style="padding: 15px; margin-bottom: 15px;">
            <h3 style="margin: 0; font-size: 1.4rem;">🎥 Gesture Recognition Stream</h3>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Model configuration selector
    st.markdown("### Inference Settings")
    model_mode = st.selectbox("Inference Model Type", ["Alphabet (Static A-Z/0-9)", "Word Model (Temporal Sequences)"], key="select_model_mode")
    
    selected_arch = st.selectbox("Sequence Architecture Model", ["LSTM", "BiLSTM", "Transformer", "TCN"], index=0, key="select_seq_arch")
    
    # Controls
    ctrl_col1, ctrl_col2, ctrl_col3 = st.columns(3)
    with ctrl_col1:
        if st.button("Start AI Predictor", key="btn_start_gest_cam"):
            st.session_state["gesture_cam_active"] = True
            st.session_state["predictions_log"].clear()
            st.session_state["sequence_buffer"].clear()
            st.session_state["gesture_sentence"] = ""
    with ctrl_col2:
        if st.button("Stop Predictor", key="btn_stop_gest_cam"):
            st.session_state["gesture_cam_active"] = False
    with ctrl_col3:
        if st.button("Reset Timeline", key="btn_clear_gest_seq"):
            st.session_state["predictions_log"].clear()
            st.session_state["sequence_buffer"].clear()
            st.session_state["gesture_sentence"] = ""
            st.success("Buffer cleared!")

    video_view = st.empty()
    
    if st.session_state["gesture_cam_active"]:
        st.markdown('<div class="pulse-badge">● REAL-TIME CLASSIFIER BROADCASTING</div>', unsafe_allow_html=True)
        
        # Start camera manager
        success = perception_service.camera.initialize_camera(sys_config.camera.source_index)
        if success:
            try:
                while st.session_state["gesture_cam_active"]:
                    read_success, frame, latency = perception_service.camera.read_frame()
                    if not read_success:
                        st.error("Ingestion failed: Camera disconnected.")
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
                                    st.success(f"Recorded 1 sample sequence successfully: {saved_path.name}")
                                else:
                                    st.error("Recording failed validation filters.")

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
                            st.session_state["sequence_buffer"], visibility, quality, occlusion, stability
                        )
                        
                    # Log prediction history
                    pred_label = prediction_data["prediction"]
                    pred_conf = prediction_data["confidence"]
                    
                    if pred_label not in ["IDLE", "WAITING_FOR_CLEAR_GESTURE", ""]:
                        # Append to history logs
                        if not st.session_state["predictions_log"] or st.session_state["predictions_log"][-1]["prediction"] != pred_label:
                            st.session_state["predictions_log"].append({
                                "prediction": pred_label,
                                "timestamp": time.strftime("%H:%M:%S"),
                                "confidence": pred_conf
                            })
                            # Limit history size
                            if len(st.session_state["predictions_log"]) > 10:
                                st.session_state["predictions_log"].pop(0)
                                
                            # Reconstruct phrase
                            st.session_state["gesture_sentence"] = " ".join([item["prediction"] for item in st.session_state["predictions_log"]])

                    # Mirror and render frame
                    display_img = cv2.flip(frame, 1)
                    if telemetry_data.landmarks.pose.present:
                        display_img = perception_service.pose_det.mp_pose.solutions.drawing_utils.draw_landmarks(
                            display_img, 
                            telemetry_data.landmarks.pose.landmarks,
                            None
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
            st.error("Capture device initialization failed.")
    else:
        video_view.info("Start the AI Predictor camera loop to initiate real-time gesture classification.")

# ----------------- RIGHT COLUMN: CONTROL PANELS & STUDIO -----------------
with col_panels:
    tab_recognition, tab_training, tab_registry = st.tabs(["🤟 AI Predictions", "🏋️ Custom Training Studio", "🛡️ Model Registry"])
    
    with tab_recognition:
        # Display classification results
        curr_pred = prediction_data["prediction"]
        curr_conf = prediction_data["confidence"]
        
        st.markdown(
            f"""
            <div class="bauhaus-card card-blue" style="padding:20px; margin-bottom:15px; text-align: center;">
                <h4 style="margin:0 0 5px 0; font-size:1.1rem; color:#D02020 !important;">ACTIVE GESTURE CLASSIFIED</h4>
                <h1 style="font-size:3.5rem; letter-spacing: -2px; margin: 5px 0;">{curr_pred}</h1>
                <div style="background-color:#E6E6E6; height:20px; border:2px solid #121212; position:relative; margin-top:10px;">
                    <div style="background-color:#F0C020; height:100%; width:{int(curr_conf * 100)}%; border-right:2px solid #121212;"></div>
                </div>
                <div style="display:flex; justify-content:space-between; margin-top:5px; font-weight:bold; font-size:0.85rem;">
                    <span>CONFIDENCE:</span><span>{int(curr_conf * 100)}%</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Alternatives
        alts = prediction_data.get("alternatives", [])
        alt_str = ", ".join(alts) if alts else "None"
        st.markdown(f"**Top Alternatives Candidates:** `{alt_str}`")

        # Sentence output
        phrase = st.session_state["gesture_sentence"]
        st.markdown("### Decoded Sentence Output")
        st.markdown(
            f"""
            <div class="bauhaus-card card-yellow" style="min-height: 80px; background-color: #FFFFFF !important;">
                <p style="font-size: 1.35rem; font-weight: 800; text-transform: uppercase; margin: 0; color: #121212;">
                    {phrase if phrase else "Waiting for continuous signing..."}
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

        # History log table
        st.markdown("### Recent Gestures Timeline")
        if st.session_state["predictions_log"]:
            df_hist = pd.DataFrame(st.session_state["predictions_log"])
            st.dataframe(df_hist, use_container_width=True, hide_index=True)
        else:
            st.write("*No gestures registered in active buffer*")

    with tab_training:
        st.markdown("### Create Custom Gesture Label")
        custom_label = st.text_input("Enter Gesture Name:", value="GREETING", id="input_custom_train_label")
        
        # Recording controller
        st.markdown("#### Record Landmark Dataset")
        st.markdown("Before recording, make sure your body is in view. Pressing Start will start a 3-second countdown, then record 30 frames.")
        
        if st.button("🔴 Start Custom Recording", key="btn_start_custom_rec", disabled=st.session_state["custom_rec_active"]):
            st.session_state["custom_rec_active"] = True
            st.session_state["rec_frame_count"] = 0
            
            # Start recorder session
            gesture_service.start_recording(custom_label)
            st.info("Recording countdown starting in main camera feed...")

        # Training panel trigger
        st.markdown("---")
        st.markdown("#### Compile & Train Gesture Model")
        st.markdown("Trigger training using PyTorch. If no recorded samples exist, the system will auto-generate synthetic sequence features.")
        
        train_epochs = st.slider("Epochs count", min_value=5, max_value=50, value=15, step=5)
        train_batch = st.select_slider("Batch Size", options=[8, 16, 32], value=16)
        train_lr = st.selectbox("Learning Rate", [0.01, 0.001, 0.0001], index=1)
        
        if st.button("🏋️ Run Neural Net Training", key="btn_trigger_pytorch_train", use_container_width=True):
            with st.spinner("Training PyTorch classifier..."):
                version, metrics = gesture_service.train_gesture_model(
                    model_type="word",
                    arch_name=selected_arch,
                    epochs=train_epochs,
                    batch_size=train_batch,
                    lr=train_lr
                )
                st.success(f"Model successfully trained and saved! Version: **{version}**")
                st.markdown(
                    f"""
                    <div style="background-color:#FFFFFF; border:3px solid #121212; padding:15px; color:#121212 !important;">
                        <strong>Test Set Accuracy:</strong> {round(metrics['accuracy'] * 100, 2)}%<br/>
                        <strong>Macro F1 Score:</strong> {round(metrics['f1_score'] * 100, 2)}%
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        # Dataset Inventory stats
        st.markdown("---")
        st.markdown("#### Dataset Inventory Counts")
        stats = gesture_service.get_dataset_stats()
        if stats:
            df_stats = pd.DataFrame(list(stats.items()), columns=["Label", "Repetitions"])
            st.dataframe(df_stats, use_container_width=True, hide_index=True)
            
            label_to_delete = st.selectbox("Select label to clear:", options=list(stats.keys()), id="select_delete_label")
            if st.button("🗑️ Delete Samples for Label", key="btn_delete_samples_label"):
                if gesture_service.clear_dataset_label(label_to_delete):
                    st.success(f"Deleted samples for label '{label_to_delete}'")
                    st.rerun()
        else:
            st.write("*No recorded datasets present.*")

    with tab_registry:
        st.markdown("### Active Models Configuration")
        reg_status = gesture_service.get_registry_status()
        
        active_alphabet = reg_status["active_alphabet"]
        active_word = reg_status["active_word"]
        
        st.markdown("**Alphabet Model:**")
        if active_alphabet:
            st.write(f"- Version: `{active_alphabet['version']}` (Accuracy: {round(active_alphabet['metrics']['test_accuracy'] * 100, 2)}%)")
        else:
            st.write("- Fallback default Alphabet MLP Active")
            
        st.markdown("**Sequence Word Model:**")
        if active_word:
            st.write(f"- Version: `{active_word['version']}` ({active_word['model_name']} - Accuracy: {round(active_word['metrics']['test_accuracy'] * 100, 2)}%)")
        else:
            st.write(f"- Fallback default Word {selected_arch} Active")

        # Rollback utility
        st.markdown("---")
        st.markdown("#### Model Rollback Manager")
        all_models = reg_status["all_models"]
        
        if all_models:
            model_options = [m["version"] for m in all_models]
            rollback_target = st.selectbox("Select Target Version to Restore", options=model_options, id="select_rollback_target")
            
            # Find selected model metadata
            selected_meta = next(m for m in all_models if m["version"] == rollback_target)
            st.write(f"- Type: `{selected_meta['model_type']}` | Accuracy: `{round(selected_meta['metrics']['test_accuracy'] * 100, 2)}%`")
            
            if st.button("⏪ Execute Version Rollback", key="btn_rollback_model", use_container_width=True):
                success = gesture_service.rollback_model(selected_meta["model_type"], rollback_target)
                if success:
                    st.success(f"Rollback successful! Active model set to {rollback_target}")
                    st.rerun()
                else:
                    st.error("Failed to restore target version.")
        else:
            st.write("*No previous model versions found in the registry catalog.*")

# ----------------- PANEL 6: REAL-TIME PLOTLY CHARTS -----------------
st.markdown("---")
st.markdown("### Performance & Telemetry Tracking Plots")

if st.session_state["chart_latency"] and go is not None:
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        fig_lat = go.Figure()
        fig_lat.add_trace(go.Scatter(y=st.session_state["chart_latency"], mode='lines', name='Pipeline Latency', line=dict(color='#D02020', width=3)))
        fig_lat.update_layout(title='Execution Latency (ms)', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=20, r=20, t=40, b=20), height=240)
        st.plotly_chart(fig_lat, use_container_width=True)

    with chart_col2:
        fig_conf = go.Figure()
        fig_conf.add_trace(go.Scatter(y=st.session_state["chart_confidence"], mode='lines', name='Confidence', line=dict(color='#1040C0', width=3)))
        fig_conf.update_layout(title='Classification Confidence Rating (%)', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=20, r=20, t=40, b=20), height=240)
        st.plotly_chart(fig_conf, use_container_width=True)
else:
    if st.session_state["chart_latency"]:
        st.line_chart(pd.DataFrame({
            "Latency (ms)": st.session_state["chart_latency"],
            "Confidence (%)": st.session_state["chart_confidence"]
        }))
    else:
        st.info("Line plots will display dynamically once webcam prediction activates.")
