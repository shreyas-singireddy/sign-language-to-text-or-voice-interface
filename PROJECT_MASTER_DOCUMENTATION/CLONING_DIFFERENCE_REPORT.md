# CLONING DIFFERENCE REPORT - SignBridge AI Reconstruction Blueprint

This document explains why a freshly cloned version of the SignBridge AI repository may behave differently compared to the development environment, and provides solutions for each issue.

---

## 1. Missing Model Weights Binaries (`.pt` files)

*   **Issue**: Large model files (such as PyTorch `.pt` checkpoints) are often excluded from git repositories to keep sizes manageable, or they may be corrupted during transfer.
*   **Effect**: Importing or loading model predictors fails, raising file-not-found errors during inference.
*   **Fix**:
    1.  The codebase implements a fallback mechanism: if no model checkpoint is found, the system instantiates an untrained architecture.
    2.  Use the model training cockpit to train a custom model locally, or download pre-trained checkpoints to `assets/models/`.

---

## 2. MediaPipe & Protobuf Version Mismatch

*   **Issue**: Running a standard `pip install mediapipe` without pinning package versions installs the latest MediaPipe release alongside an incompatible Protobuf version (`protobuf>=5.x`).
*   **Effect**: Streamlit crashes on startup with the following error:
    `AttributeError: module 'mediapipe' has no attribute 'solutions'`
*   **Fix**: Uninstall the mismatched packages, clear the pip cache, and force-install compatible versions:
    ```bash
    pip uninstall -y mediapipe protobuf
    pip install mediapipe==0.10.14 protobuf==4.25.9
    ```

---

## 3. Missing Local Environment Settings (`.env`)

*   **Issue**: Local configurations and credentials are excluded from the repository via `.gitignore` (`.env` and `.env.*`).
*   **Effect**: MongoDB operations fail to connect, and security-locked routes crash due to missing JWT secrets.
*   **Fix**: Copy `.env.example` to `.env` in either the project root or the `backend/` directory, and fill in the required variables (such as `MONGO_URI`).

---

## 4. Path Separator Inconsistencies (Windows vs. POSIX)

*   **Issue**: Hardcoding directory paths using backslashes (`\`) or forward slashes (`/`) can cause issues when moving between Windows and Unix-based environments.
*   **Effect**: File paths fail to resolve, causing file read/write operations to crash.
*   **Fix**: The project uses Python's `pathlib` module to handle paths dynamically, ensuring compatibility across different operating systems.

---

## 5. Web Browser & Hardware Access Permissions

*   **Issue**: Different operating systems and web browsers handle camera and audio hardware permissions differently.
*   **Effect**:
    *   OpenCV fails to access the camera stream, causing the vision pipeline to crash.
    *   Web Speech synthesis is blocked by browser security policies until the user interacts with the page.
*   **Fix**:
    *   Ensure the web browser has permission to access the camera and microphone.
    *   Verify the camera index in the settings page (typically `0` for the default camera).
