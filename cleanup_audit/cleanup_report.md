# Phase 14 Cleanup Audit Report

Generated non-destructively. No files or dependencies were deleted.

## Summary
- REQUIRED: 147 files
- POTENTIALLY UNUSED: 57 files
- SAFE TO DELETE: 155 files
- Total files scanned: 359
- Python files scanned: 172

## Safe To Delete Candidates
- `PROJECT_HEALTH_REPORT.md`
- `SPEKITE.md`
- `accessibility/__pycache__/__init__.cpython-311.pyc`
- `accessibility/__pycache__/keyboard_nav.cpython-311.pyc`
- `accessibility/__pycache__/screen_reader_hints.cpython-311.pyc`
- `accessibility/__pycache__/theme_manager.cpython-311.pyc`
- `ai_engine/__pycache__/__init__.cpython-311.pyc`
- `ai_engine/computer_vision/__pycache__/__init__.cpython-311.pyc`
- `ai_engine/computer_vision/__pycache__/camera.cpython-311.pyc`
- `ai_engine/computer_vision/__pycache__/holistic.cpython-311.pyc`
- `ai_engine/datasets/__pycache__/__init__.cpython-311.pyc`
- `ai_engine/datasets/__pycache__/dataset_manager.cpython-311.pyc`
- `ai_engine/exporters/__pycache__/__init__.cpython-311.pyc`
- `ai_engine/exporters/__pycache__/csv_exporter.cpython-311.pyc`
- `ai_engine/exporters/__pycache__/json_exporter.cpython-311.pyc`
- `ai_engine/exporters/__pycache__/parquet_exporter.cpython-311.pyc`
- `ai_engine/gesture_recognition/__pycache__/__init__.cpython-311.pyc`
- `ai_engine/gesture_recognition/__pycache__/detector.cpython-311.pyc`
- `ai_engine/gesture_recognition/dataset/__pycache__/dataset_manager.cpython-311.pyc`
- `ai_engine/gesture_recognition/dataset/__pycache__/gesture_recorder.cpython-311.pyc`
- `ai_engine/gesture_recognition/dataset/__pycache__/sample_validator.cpython-311.pyc`
- `ai_engine/gesture_recognition/features/__pycache__/landmark_features.cpython-311.pyc`
- `ai_engine/gesture_recognition/inference/__pycache__/confidence_engine.cpython-311.pyc`
- `ai_engine/gesture_recognition/inference/__pycache__/post_processor.cpython-311.pyc`
- `ai_engine/gesture_recognition/inference/__pycache__/predictor.cpython-311.pyc`
- `ai_engine/gesture_recognition/models/__pycache__/alphabet_model.cpython-311.pyc`
- `ai_engine/gesture_recognition/models/__pycache__/word_model.cpython-311.pyc`
- `ai_engine/gesture_recognition/services/__pycache__/gesture_service.cpython-311.pyc`
- `ai_engine/gesture_recognition/storage/__pycache__/checkpoint_manager.cpython-311.pyc`
- `ai_engine/gesture_recognition/storage/__pycache__/model_registry.cpython-311.pyc`
- `ai_engine/gesture_recognition/training/__pycache__/evaluator.cpython-311.pyc`
- `ai_engine/gesture_recognition/training/__pycache__/hyperparameter_tuner.cpython-311.pyc`
- `ai_engine/gesture_recognition/training/__pycache__/trainer.cpython-311.pyc`
- `ai_engine/inference/__pycache__/__init__.cpython-311.pyc`
- `ai_engine/inference/__pycache__/pipeline.cpython-311.pyc`
- `ai_engine/landmark_extraction/__pycache__/__init__.cpython-311.pyc`
- `ai_engine/landmark_extraction/__pycache__/extractor.cpython-311.pyc`
- `ai_engine/landmark_processor/__pycache__/__init__.cpython-311.pyc`
- `ai_engine/landmark_processor/__pycache__/processor.cpython-311.pyc`
- `ai_engine/processing/__pycache__/__init__.cpython-311.pyc`
- `ai_engine/processing/__pycache__/landmark_normalizer.cpython-311.pyc`
- `ai_engine/processing/__pycache__/temporal_tracker.cpython-311.pyc`
- `ai_engine/replay/__pycache__/__init__.cpython-311.pyc`
- `ai_engine/replay/__pycache__/session_replay.cpython-311.pyc`
- `ai_engine/schemas/__pycache__/__init__.cpython-311.pyc`
- `ai_engine/schemas/__pycache__/landmark_schema.cpython-311.pyc`
- `ai_engine/schemas/__pycache__/telemetry_schema.cpython-311.pyc`
- `ai_engine/sequence_models/__pycache__/__init__.cpython-311.pyc`
- `ai_engine/sequence_models/__pycache__/seq_model.cpython-311.pyc`
- `ai_engine/services/__pycache__/__init__.cpython-311.pyc`
- `ai_engine/services/__pycache__/perception_service.cpython-311.pyc`
- `ai_engine/storage/__pycache__/__init__.cpython-311.pyc`
- `ai_engine/storage/__pycache__/landmark_recorder.cpython-311.pyc`
- `ai_engine/storage/__pycache__/session_manager.cpython-311.pyc`
- `ai_engine/telemetry/__pycache__/__init__.cpython-311.pyc`
- `ai_engine/telemetry/__pycache__/motion_metrics.cpython-311.pyc`
- `ai_engine/telemetry/__pycache__/occlusion_metrics.cpython-311.pyc`
- `ai_engine/telemetry/__pycache__/performance_metrics.cpython-311.pyc`
- `ai_engine/telemetry/__pycache__/stability_metrics.cpython-311.pyc`
- `ai_engine/telemetry/__pycache__/visibility_metrics.cpython-311.pyc`
- `ai_engine/translation_engine/__pycache__/__init__.cpython-311.pyc`
- `ai_engine/translation_engine/__pycache__/translator.cpython-311.pyc`
- `ai_engine/utils/__pycache__/__init__.cpython-311.pyc`
- `ai_engine/utils/__pycache__/config.cpython-311.pyc`
- `ai_engine/utils/__pycache__/logger.cpython-311.pyc`
- `ai_engine/vision/__pycache__/__init__.cpython-311.pyc`
- `ai_engine/vision/__pycache__/camera_manager.cpython-311.pyc`
- `ai_engine/vision/__pycache__/face_detector.cpython-311.pyc`
- `ai_engine/vision/__pycache__/hand_detector.cpython-311.pyc`
- `ai_engine/vision/__pycache__/pose_detector.cpython-311.pyc`
- `ai_engine_audit.md`
- `analytics/__pycache__/__init__.cpython-311.pyc`
- `analytics/__pycache__/heatmap_builder.cpython-311.pyc`
- `analytics/__pycache__/metrics_collector.cpython-311.pyc`
- `analytics/__pycache__/report_generator.cpython-311.pyc`
- `api_audit.md`
- `app/__pycache__/__init__.cpython-311.pyc`
- `app/__pycache__/main.cpython-311.pyc`
- `app/pages/__pycache__/accessibility.cpython-311.pyc`
- `app/pages/__pycache__/admin.cpython-311.pyc`
- `app/pages/__pycache__/analytics.cpython-311.pyc`
- `app/pages/__pycache__/communication_hub.cpython-311.pyc`
- `app/pages/__pycache__/emergency.cpython-311.pyc`
- `app/pages/__pycache__/home.cpython-311.pyc`
- `app/pages/__pycache__/live_translation.cpython-311.pyc`
- `app/pages/__pycache__/settings.cpython-311.pyc`
- `app/pages/__pycache__/training_studio.cpython-311.pyc`
- `app/services/__pycache__/__init__.cpython-311.pyc`
- `app/services/__pycache__/ai_service.cpython-311.pyc`
- `app/services/__pycache__/audio_service.cpython-311.pyc`
- `app/services/__pycache__/database_service.cpython-311.pyc`
- `backend/app/__pycache__/__init__.cpython-311.pyc`
- `backend/app/__pycache__/main.cpython-311.pyc`
- `backend/app/api/__pycache__/__init__.cpython-311.pyc`
- `backend/app/api/__pycache__/admin.cpython-311.pyc`
- `backend/app/api/__pycache__/auth.cpython-311.pyc`
- `backend/app/api/__pycache__/live.cpython-311.pyc`
- `backend/app/api/__pycache__/translate.cpython-311.pyc`
- `backend/app/api/__pycache__/utils.cpython-311.pyc`
- `backend/app/api/v1/__pycache__/__init__.cpython-311.pyc`
- `backend/app/api/v1/__pycache__/auth.cpython-311.pyc`
- `backend/app/api/v1/__pycache__/router.cpython-311.pyc`
- `backend/app/core/__pycache__/__init__.cpython-311.pyc`
- `backend/app/core/__pycache__/config.cpython-311.pyc`
- `backend/app/core/__pycache__/database.cpython-311.pyc`
- `backend/app/core/__pycache__/security.cpython-311.pyc`
- `backend/app/data/__pycache__/live_feed.cpython-311.pyc`
- `backend/app/db/__pycache__/__init__.cpython-311.pyc`
- `backend/app/db/__pycache__/client.cpython-311.pyc`
- `backend/app/db/__pycache__/schemas.cpython-311.pyc`
- `backend/app/schemas/__pycache__/__init__.cpython-311.pyc`
- `backend/app/schemas/__pycache__/auth.cpython-311.pyc`
- `backend/app/services/__pycache__/__init__.cpython-311.pyc`
- `backend/app/services/__pycache__/translate_service.cpython-311.pyc`
- `backend/app/utils/__pycache__/__init__.cpython-311.pyc`
- `backend/app/utils/__pycache__/image_decoder.cpython-311.pyc`
- `backend/app/utils/__pycache__/mediapipe_model.cpython-311.pyc`
- `backend/ws/__pycache__/telemetry_socket.cpython-311.pyc`
- `config/__pycache__/__init__.cpython-311.pyc`
- `config/__pycache__/config.cpython-311.pyc`
- `config/__pycache__/logger.cpython-311.pyc`
- `cv_stability_report.md`
- `database/__pycache__/__init__.cpython-311.pyc`
- `database/__pycache__/mongodb.cpython-311.pyc`
- `database_audit.md`
- `dataset_health_report.md`
- `dependency_report.md`
- `frontend/.vite/deps/_metadata.json`
- `frontend/.vite/deps/package.json`
- `frontend/pages/__pycache__/live_gesture_recognition.cpython-311.pyc`
- `frontend/pages/__pycache__/live_vision_engine.cpython-311.pyc`
- `gesture_accuracy_report.md`
- `import_audit.md`
- `integration_report.md`
- `speech/__pycache__/__init__.cpython-311.pyc`
- `speech/__pycache__/schemas.cpython-311.pyc`
- `speech/__pycache__/stt_engine.cpython-311.pyc`
- `speech/__pycache__/tts_engine.cpython-311.pyc`
- `speech/__pycache__/voice_profile.cpython-311.pyc`
- `speech/__pycache__/whisper_engine.cpython-311.pyc`
- `speech/providers/__pycache__/__init__.cpython-311.pyc`
- `speech/providers/__pycache__/base.cpython-311.pyc`
- `speech/providers/__pycache__/browser_provider.cpython-311.pyc`
- `speech/providers/__pycache__/gtts_provider.cpython-311.pyc`
- `static_analysis_report.md`
- `streamlit_audit.md`
- `translation/__pycache__/__init__.cpython-311.pyc`
- `translation/__pycache__/context_manager.cpython-311.pyc`
- `translation/__pycache__/engine.cpython-311.pyc`
- `translation/__pycache__/grammar_fixer.cpython-311.pyc`
- `translation/__pycache__/schemas.cpython-311.pyc`
- `translation/providers/__pycache__/__init__.cpython-311.pyc`
- `translation/providers/__pycache__/base.cpython-311.pyc`
- `translation/providers/__pycache__/google_adapter.cpython-311.pyc`
- `translation/providers/__pycache__/rule_based.cpython-311.pyc`

## Potentially Unused Source/Data Candidates
- `ai_engine/dataset_manager/recorder.py`: No static import/reference found; review before deleting.
- `ai_engine/pipeline/vision_pipeline.py`: No static import/reference found; review before deleting.
- `backend/app/db/schemas.py`: No static import/reference found; review before deleting.
- `backend/ws/telemetry_socket.py`: No static import/reference found; review before deleting.
- `communication/hub.py`: No static import/reference found; review before deleting.
- `frontend/Dockerfile`: No static import/reference found; review before deleting.
- `frontend/src/components/.gitkeep`: No static import/reference found; review before deleting.
- `frontend/src/context/.gitkeep`: No static import/reference found; review before deleting.
- `frontend/src/context/AuthContext.tsx`: No static import/reference found; review before deleting.
- `frontend/src/context/ThemeContext.tsx`: No static import/reference found; review before deleting.
- `frontend/src/hooks/.gitkeep`: No static import/reference found; review before deleting.
- `frontend/src/pages/.gitkeep`: No static import/reference found; review before deleting.
- `frontend/src/services/.gitkeep`: No static import/reference found; review before deleting.
- `frontend/src/utils/.gitkeep`: No static import/reference found; review before deleting.
- `frontend/src/vite-env.d.ts`: No static import/reference found; review before deleting.
- `frontend/tsconfig.json`: No static import/reference found; review before deleting.

## Required / Protected Surfaces
- Never delete: `.env`, `requirements.txt`, `frontend/package.json`, `docker-compose.yml`, `main.py` files, FastAPI routes, Streamlit pages, auth/database files, active model registry files.
- Required entry points detected: `app/main.py`, `backend/app/main.py`, `frontend/src/main.tsx`, `frontend/src/App.tsx`, `run_full_audit.py`.
- Required app surfaces detected: `app/pages/*.py`, `frontend/pages/*.py`, `backend/app/api/**`, tests, Docker files, Vite/TypeScript/Tailwind configs.

## Dead Code Review Candidates
These are heuristic candidates with no external and no same-file name references. Review manually before removing.
- `accessibility/keyboard_nav.py:54` function `get_all_shortcuts`
- `accessibility/keyboard_nav.py:58` function `get_shortcuts_by_modifier`
- `accessibility/screen_reader_hints.py:56` function `status_badge`
- `accessibility/screen_reader_hints.py:92` function `skip_to_content_link`
- `accessibility/screen_reader_hints.py:121` function `landmark_region`
- `accessibility/screen_reader_hints.py:135` function `image_description`
- `accessibility/theme_manager.py:136` function `get_all_themes`
- `accessibility/theme_manager.py:140` function `get_theme_description`
- `ai_engine/computer_vision/camera.py:55` function `is_running`
- `ai_engine/dataset_manager/recorder.py:30` function `pause_session`
- `ai_engine/dataset_manager/recorder.py:36` function `resume_session`
- `ai_engine/dataset_manager/recorder.py:42` function `capture_frame`
- `ai_engine/dataset_manager/recorder.py:53` function `stop_session`
- `ai_engine/dataset_manager/recorder.py:71` function `export_dataset`
- `ai_engine/gesture_recognition/dataset/dataset_manager.py:175` function `export_dataset_files`
- `ai_engine/gesture_recognition/features/motion_features.py:4` function `compute_velocities`
- `ai_engine/gesture_recognition/features/motion_features.py:13` function `compute_accelerations`
- `ai_engine/gesture_recognition/features/motion_features.py:21` function `compute_hand_direction`
- `ai_engine/gesture_recognition/features/motion_features.py:41` function `extract_motion_telemetry`
- `ai_engine/gesture_recognition/features/temporal_features.py:4` function `compute_trajectory_length`
- `ai_engine/gesture_recognition/features/temporal_features.py:41` function `compute_rolling_summary`
- `ai_engine/gesture_recognition/features/temporal_features.py:58` function `get_gesture_duration`
- `ai_engine/gesture_recognition/inference/post_processor.py:28` function `suppress_false_positives`
- `ai_engine/gesture_recognition/models/sentence_model.py:35` function `decode_transitions`
- `ai_engine/gesture_recognition/models/word_model.py:186` function `benchmark_model`
- `ai_engine/gesture_recognition/schemas/prediction_schema.py:4` class `AlphabetPredictionResponse`
- `ai_engine/gesture_recognition/schemas/prediction_schema.py:9` class `WordPredictionResponse`
- `ai_engine/gesture_recognition/schemas/prediction_schema.py:13` class `SentencePredictionResponse`
- `ai_engine/gesture_recognition/services/gesture_service.py:67` function `tune_model`
- `ai_engine/gesture_recognition/storage/checkpoint_manager.py:24` function `load_checkpoint`
- `ai_engine/gesture_recognition/training/evaluator.py:59` function `export_report`
- `ai_engine/inference_preparation/preprocessor.py:11` function `pad_sequence`
- `ai_engine/pipeline/vision_pipeline.py:31` function `run_perception`
- `ai_engine/vision/camera_manager.py:116` function `switch_camera`
- `analytics/heatmap_builder.py:76` function `build_word_heatmap`
- `analytics/metrics_collector.py:61` function `record_translation`
- `analytics/metrics_collector.py:109` function `record_speech_synthesis`
- `analytics/report_generator.py:130` function `generate_performance_report`
- `app/services/ai_service.py:20` function `get_pipeline_status`
- `app/services/audio_service.py:24` function `speech_to_text`
- `app/services/audio_service.py:34` function `get_voice_options`
- `backend/app/api/deps.py:9` function `get_current_user`
- `backend/app/db/schemas.py:23` class `TranslationInput`
- `backend/app/db/schemas.py:27` class `TranslationRecord`
- `backend/ws/telemetry_socket.py:35` function `websocket_endpoint`
- `backend/ws/telemetry_socket.py:21` function `broadcast_telemetry`
- `communication/hub.py:24` function `post_message`
- `communication/hub.py:42` function `get_session_transcript`
- `conversation/dialogue_manager.py:193` function `get_active_session_count`
- `conversation/dialogue_manager.py:197` function `get_all_session_ids`
- `conversation/emotion_tone.py:164` function `get_ui_color`
- `conversation/message_thread.py:98` function `add_system_message`
- `conversation/message_thread.py:125` function `get_last_n_messages`
- `conversation/message_thread.py:141` function `get_full_thread`
- `emergency/alert_dispatcher.py:126` function `get_alert_history`
- `emergency/alert_dispatcher.py:138` function `clear_history`
- `emergency/alert_dispatcher.py:143` function `configure_webhook`
- `emergency/emergency_phrases.py:144` function `get_emergency_phrase`
- `emergency/panic_protocol.py:153` function `get_activation_count`
- `emergency/panic_protocol.py:157` function `get_activation_history`
- `emergency/panic_protocol.py:184` function `generate_quick_sos_html`
- `emergency/sos_detector.py:172` function `get_last_event`
- `emergency/sos_detector.py:176` function `get_event_count`
- `emergency/sos_detector.py:180` function `reset_window`
- `multilingual/language_registry.py:131` function `get_all`
- `multilingual/language_registry.py:135` function `get_names`
- `multilingual/language_registry.py:139` function `get_rtl_languages`
- `multilingual/language_registry.py:143` function `get_languages_by_region`
- `multilingual/language_registry.py:147` function `get_bcp47`
- `multilingual/language_registry.py:152` function `get_tts_code`
- `multilingual/language_registry.py:162` function `get_flag`
- `multilingual/language_registry.py:167` function `get_native_name`
- `multilingual/language_registry.py:172` function `get_selectbox_options`
- `multilingual/locale_formatter.py:50` function `format_confidence`
- `multilingual/locale_formatter.py:65` function `format_date`
- `multilingual/locale_formatter.py:85` function `format_duration`
- `multilingual/locale_formatter.py:103` function `get_ui_strings`
- `multilingual/rtl_handler.py:41` function `wrap_rtl_text`
- `multilingual/rtl_handler.py:58` function `get_rtl_css`
- `multilingual/rtl_handler.py:74` function `apply_to_bauhaus_card`
- ... 12 more heuristic candidates omitted from this report.

## Dependency Cleanup
### Root Python `requirements.txt`
- Keep current imported packages: `streamlit`, `opencv-python`, `mediapipe`, `pymongo[srv]`, `python-dotenv`, `numpy`, `pandas`, `pytest`, `httpx`, `plotly`, `gTTS`.
- Add missing runtime/audit dependency: `psutil>=5.9.0` because `run_full_audit.py` imports `psutil`.
- No root Python dependency was proven unused by import scan.

### Backend `backend/requirements.txt`
- Keep FastAPI backend dependencies: `fastapi`, `uvicorn`, `pydantic`, `pydantic-settings`, `motor`, `python-jose`, `passlib`, `bcrypt`, `python-multipart`, `python-dotenv`, `mediapipe`, `opencv-python`, `numpy`, `scikit-learn`, `pandas`, `pytest`, `httpx`.
- `python-multipart` is not directly imported; keep for FastAPI form/file handling unless auth/upload endpoints are permanently removed.

### Frontend `package.json`
- Remove candidate: `lucide-react`; no import found in `frontend/src` or config.
- Keep `@types/react` and `@types/react-dom`; they are TypeScript build-time packages even when not imported directly.
- Cleaned suggestions written to `cleanup_audit/package.cleaned.json`.

## Model File Audit
- No `.pt`, `.pth`, or `.h5` model binaries were found in the scanned repository outside ignored dependency/cache folders.
- `assets/models/registry/registry_metadata.json` is REQUIRED; it is referenced by `ai_engine/gesture_recognition/storage/model_registry.py`.
- Registry references model paths such as `v_word_*/dummy.pt`, but those binaries are not present in the current scan.

## Asset Cleanup
- Required data: `ai_engine/datasets/data/dataset_index.json`, `ai_engine/datasets/data/offline_history.json`.
- Safe local cache: `frontend/.vite/` if present. It is generated by Vite and can be recreated.
- Safe Python caches: any `__pycache__/` files. They are interpreter-generated and can be recreated.
- No image/video/audio assets were found in the scanned project tree.

## Backup List
- Written to `cleanup_audit/backup_list.txt`. This is the exact deletion candidate list for a later cleanup pass.

## Cleanup Execution Status
- Deleted files: none
- Deleted dependencies: none
- Deleted assets: none
- Updated imports: none
- Updated requirements/package configuration: no live files updated; cleaned proposal files generated only

## Verification Notes
- This audit was static and non-destructive.
- Lightweight compile check passed for `app/main.py`, `frontend/pages/live_vision_engine.py`, and `frontend/pages/live_gesture_recognition.py`.
- `python -m pytest` did not complete: collection failed because tests import two conflicting `app` package layouts (`backend/tests/test_pipeline.py` expects `app.utils.mediapipe_model`; `tests/test_scaffolding.py` expects root `app.services.database_service`).
- `cd frontend && npm run build` did not complete: TypeScript cannot resolve `frontend/src/types` imported by `frontend/src/context/AuthContext.tsx`.
- Runtime endpoint checks returned HTTP 200 for Streamlit `http://localhost:8501`, FastAPI `http://localhost:8000`, and Vite `http://localhost:4173`.
- After any deletion pass, rerun: `python -m pytest`, `cd frontend && npm run build`, `streamlit run app\main.py`, backend `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`, frontend `npm run dev -- --host 0.0.0.0 --port 4173`.

## Rollback Instructions
1. Restore deleted files from git: `git restore -- <path>` for tracked files.
2. Restore dependency manifests from git: `git restore requirements.txt frontend/package.json frontend/package-lock.json`.
3. Reinstall dependencies if manifests change: `pip install -r requirements.txt`; `cd frontend && npm install`.
4. Recreate caches naturally by running Python/Streamlit/Vite; do not commit cache folders.
