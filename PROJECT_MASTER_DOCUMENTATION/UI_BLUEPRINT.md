# UI BLUEPRINT - SignBridge AI Reconstruction Blueprint

This document details the user interface design system, styling structures, layout configurations, and styling behaviors of the SignBridge AI application.

---

## 1. Visual Theme & Styling System

The application uses a **Bauhaus-Constructivist Design System** featuring high-contrast geometric lines, thick borders, solid primary color accents (Bauhaus red, blue, and yellow), and distinct micro-animations.

### 1.1 Styling Parameters

*   **Primary Fonts**:
    *   *Headers*: `Space Grotesk`, sans-serif (heavy uppercase weighting: `900`).
    *   *Body / Controls*: `Outfit`, sans-serif.
*   **Colors**:
    *   `#F0F0F0`: Base page background.
    *   `#121212`: Text, borders, headers, and primary box outlines.
    *   `#FFFFFF`: Main card content background.
    *   `#D02020`: Bauhaus Red (Accent 1, Sidebar trim, errors).
    *   `#1040C0`: Bauhaus Blue (Accent 2, Info nodes, indicators).
    *   `#F0C020`: Bauhaus Yellow (Accent 3, Buttons, warnings).

### 1.2 Global CSS Styling Injection
Injected at application startup via [app/main.py](file:///C:/Users/shrey/Downloads/hack2/sign-language-to-text-or-voice-translator/app/main.py#L25-L206):

```css
/* Bauhaus Containers */
.bauhaus-card {
    background-color: #FFFFFF !important;
    border: 3.5px solid #121212 !important;
    box-shadow: 8px 8px 0px #121212 !important;
    padding: 30px;
    margin-bottom: 25px;
    position: relative;
    transition: all 0.2s ease-in-out;
}
.bauhaus-card:hover {
    transform: translate(-3px, -3px);
    box-shadow: 11px 11px 0px #121212 !important;
}

/* Bold Buttons */
.stButton>button {
    font-family: 'Space Grotesk', sans-serif !important;
    text-transform: uppercase !important;
    font-weight: 800 !important;
    border: 3.5px solid #121212 !important;
    border-radius: 0px !important;
    box-shadow: 4px 4px 0px #121212 !important;
    background-color: #F0C020 !important;
    color: #121212 !important;
}
.stButton>button:hover {
    background-color: #D02020 !important;
    color: #FFFFFF !important;
    box-shadow: 6px 6px 0px #121212 !important;
}
```

---

## 2. Multi-Page Layout Registry

### 2.1 Splash Screen & Registration
Before accessing the main workspace, a mandatory sequence router is executed:
1.  **Splash Screen Card**: Displays title, dynamic CSS shapes composition, and "Enter" CTA.
2.  **Registration Card**: Form fields for Name and Phone.
3.  **OTP Simulation Dialog**: Displays a simulated passcode (`1919`) to verify the identity.
4.  **Welcome Dispatcher**: Confirms authentication and unlocks dashboard navigation.

### 2.2 Home landing Page
*   **Pipeline Grid**: Three primary blocks mapping the translation stages:
    *   *Skeletons Extraction*: MediaPipe holistic parser indicators.
    *   *Distortions Filters*: Normalizer algorithms.
    *   *Target Mappings*: PyTorch classification results.

### 2.3 Vision Mission Control (`live_vision_engine.py`)
*   **Source Switcher**: Radio button toggling between Live Camera and Session Replay.
*   **Ingestion Feed**: Standard video element displaying the webcam frame with joints overlay.
*   **Performance Telemetry**: Multi-column tables tracking FPS, elbow joint angles, and tracking stability.
*   **Charts Panel**: Plotly graphs plotting FPS and hand velocity trends over time.

### 2.4 Gesture Control Cockpit (`live_gesture_recognition.py`)
*   **Model Configurer**: Selectbox inputs configuring dynamic architectures (LSTM, BiLSTM, TCN, or Transformer).
*   **Predictions Stream**: Displays active classification labels in a yellow card. Shows classification confidence.
*   **Dataset Recorder**: Sub-tabs for recording new custom gesture datasets.

### 2.5 Live Translation
*   **Output Box**: Standard text field displaying the translation sentence.
*   **Voice Switcher**: Sliders controlling TTS rate, pitch, and voice gender profiles.

### 2.6 Analytics Platform
*   **Charts Grid**: High-contrast Plotly bar charts displaying translations frequency, language distributions, and daily activity.

---

## 3. Viewport & Cross-Platform Scaling Analysis

The interface may display layout shifts across different machines due to the following factors:

*   **Display Scaling (DPI)**: High-DPI screens (e.g., Retina displays or Windows settings at `125%` or `150%`) can expand the thick Bauhaus borders, which can push adjacent columns into vertical layouts.
*   **Streamlit Column Ratios**: Page layouts use `st.columns([1, 1])` and `st.columns([1, 2, 1])`. In narrow viewports, Streamlit wraps these columns vertically, altering the layout.
*   **Fonts Fallback**: If a system is offline and cannot fetch fonts from `fonts.googleapis.com`, it falls back to standard `sans-serif` or `Arial`, which can alter text alignment.
*   **Plotly Resizing**: Plotly figures use `use_container_width=True`. When a sidebar is toggled open or closed, the graphs automatically re-render to fit the container.
