# SignBridge AI: End-User & Operator Manual

Welcome to SignBridge AI! This guide outlines how to operate, configure, navigate, and troubleshoot the SignBridge AI application.

---

## 🖥️ Launching the Application

### 1. Developer Perception Portal (Streamlit)
To start the developer console which displays webcam feed overlay tracking, landmark telemetry, and gesture models:
```bash
backend\.venv\Scripts\python.exe -m streamlit run app/main.py --server.port 8501
```
Open your web browser and navigate to `http://localhost:8501`.

### 2. High-Fidelity Client Interface (React + Vite)
To start the web client app:
1. Ensure the backend API is running (see [README.md](file:///README.md#running-the-application)).
2. Start the local server:
   ```bash
   cd frontend
   npm run dev -- --host 0.0.0.0 --port 4173
   ```
3. Open your browser and navigate to `http://localhost:4173`.

---

## 🧭 Navigating the System

### 1. Account Portal
- **Registration**: Enter your name, email address, and password.
- **Login**: Log in to obtain a secure session token.
- **Session Management**: Tokens expire after 24 hours. Use the logout button to clear your credentials.

### 2. Real-Time Translation Interface
- **Webcam Feed**: Toggle your camera on/off using the camera icon.
- **Gesture Landmark Tracking**: Real-time overlays (hands, face, pose landmarks) indicate successful camera capture.
- **Vocalized Translation Output**: The translated text is displayed on-screen, and a synthesized text-to-speech voice is automatically played through your system audio output.
- **Translation Settings**: Use the control panel side drawer to change the output language or adjust the text-to-speech volume and speaking rate.

### 3. Historical Logs & Analytics Dashboard
- Navigate to the **History** tab to see past translations.
- Filter by date or search for specific words.
- Export logs as JSON or CSV files using the **Export** button at the top-right of the log table.

---

## 🎨 Accessibility Options & Themes

SignBridge AI is designed with accessibility at its core:
- **Theme Selection**: Toggle between **Dark Mode** (vibrant neon green/dark slate palettes) and **Light Mode** (high-contrast indigo/white) via the top-navigation profile bar.
- **Contrast Enhancements**: Customize contrast thresholds and font sizes in the user profile settings dashboard.
- **Speech Controls**: Choose your preferred output voice, rate of speech, and language locale.

---

## 🔍 Troubleshooting Webcam & Feed Failures

### 1. Browser Permission Errors
If the webcam feed displays a blank box or a warning icon:
- **Chrome/Firefox**: Look for the camera icon in your address bar. Verify that permissions are set to "Allow" for `http://localhost:8501` and `http://localhost:4173`.
- **System Level**: On Windows/macOS, check system privacy settings to ensure the browser has permission to access the camera.

### 2. Streamlit Video Frame Drops / High Latency
- If the overlay rendering lags or stutter occurs:
  - Close other high-performance applications.
  - Decrease camera input resolution in the developer console sidebar (e.g. from 1080p to 720p).
  - Ensure your machine's graphics card drivers are updated (PyTorch uses GPU hardware acceleration if CUDA is available).

### 3. MediaPipe Errors
- If the message `AttributeError: module 'mediapipe' has no attribute 'solutions'` is displayed in the terminal:
  - Run the following commands to install the exact compatible packages:
    ```bash
    pip install mediapipe==0.10.14 protobuf==4.25.9
    ```
