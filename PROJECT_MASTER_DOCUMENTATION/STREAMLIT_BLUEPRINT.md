# STREAMLIT BLUEPRINT - SignBridge AI Reconstruction Blueprint

This document details the page structures, routing logic, state properties, and server setups of the Streamlit frontend.

---

## 1. Page Navigation Registry & Multipage Routing

Multipage routing is managed inside [app/main.py](file:///C:/Users/shrey/Downloads/hack2/sign-language-to-text-or-voice-translator/app/main.py) using Streamlit's `st.navigation` engine.

*   **Primary Application Pages**:
    *   `app/pages/home.py`: App landing dashboard.
    *   `frontend/pages/live_vision_engine.py`: Raw camera joint tracking and session replay portal.
    *   `frontend/pages/live_gesture_recognition.py`: Real-time gesture classification control cockpits.
    *   `app/pages/live_translation.py`: Formatted translation and voice synthesis controls.
    *   `app/pages/training_studio.py`: Model training configurations.
    *   `app/pages/communication_hub.py`: Messaging streams and user rooms.
    *   `app/pages/analytics.py`: Plotly charts.
    *   `app/pages/accessibility.py`: Accessibility profiles and screen reader configurations.
    *   `app/pages/emergency.py`: SOS trigger options.
    *   `app/pages/settings.py`: Port index setups and system values.
    *   `app/pages/admin.py`: Administration credentials and database resetting controls.

---

## 2. Session State Registry

The frontend manages user interactions and telemetry buffers using the following session state variables:

| Variable Key | Expected Type | Initial Value | Purpose / Usage |
| :--- | :--- | :--- | :--- |
| `authenticated` | `bool` | `False` | Blocks access to dashboard pages until the login flow is complete. |
| `auth_step` | `str` | `"splash"` | Tracks login flow steps: `"splash"`, `"login"`, `"otp"`, `"welcome"`, or `"dashboard"`. |
| `user_name` | `str` | `""` | Stores the user's name entered during registration. |
| `user_phone` | `str` | `""` | Stores the mobile number used for simulated OTP verification. |
| `cam_active` | `bool` | `False` | Tracks if the vision engine camera capture loop is active. |
| `rec_active` | `bool` | `False` | Tracks if landmark recording is active. |
| `gesture_cam_active`| `bool` | `False` | Tracks if the gesture classification camera capture loop is active. |
| `custom_rec_active` | `bool` | `False` | Tracks if custom landmark sequence training recording is active. |
| `predictions_log` | `list` | `[]` | Stores recent predictions to display in the gesture history timeline. |
| `gesture_sentence` | `str` | `""` | Reconstructs predicted words into a unified sentence. |
| `sequence_buffer` | `list` | `[]` | Stores landmark frames for sequence classification. |
| `chart_latency` | `list` | `[]` | Latency buffer values plotted in the performance charts. |
| `chart_confidence` | `list` | `[]` | Confidence buffer values plotted in the performance charts. |

---

## 3. Styles & Injected Custom CSS overrides

Styling customizations are injected globally via [app/main.py](file:///C:/Users/shrey/Downloads/hack2/sign-language-to-text-or-voice-translator/app/main.py#L25-L206).

*   **Bauhaus Typography Overrides**:
    *   Fonts are imported from Google Fonts: Space Grotesk and Outfit.
    *   Headers default to `Space Grotesk` with `900` weight.
*   **Stark Buttons Layout**:
    *   Thick borders (`3.5px solid #121212`), no round corners (`border-radius: 0px`), offset shadow (`4px 4px 0px #121212`), and yellow background (`#F0C020`).
*   **Bauhaus Card Elements**:
    *   White background, thick black borders, and shift transition transformations on hover:
    ```css
    .bauhaus-card:hover {
        transform: translate(-3px, -3px);
        box-shadow: 11px 11px 0px #121212 !important;
    }
    ```

---

## 4. Startup & Execution Requirements

To launch the Streamlit frontend with clean path imports, run the following:

1.  **Bootstrap Path Setup**: Before running imports, the root path is prepended to `sys.path` in [app/main.py](file:///C:/Users/shrey/Downloads/hack2/sign-language-to-text-or-voice-translator/app/main.py#L4-L7):
    ```python
    PROJECT_ROOT = Path(__file__).resolve().parent.parent
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))
    ```
2.  **Server Startup Command**: Launch the dev server on port `8501`:
    ```bash
    backend\.venv\Scripts\python.exe -m streamlit run app/main.py --server.port 8501
    ```
