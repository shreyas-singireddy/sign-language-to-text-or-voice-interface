# DEPENDENCY MANIFEST - SignBridge AI Reconstruction Blueprint

This document details the software package dependencies, virtual environment configurations, and version compatibility matrices of the SignBridge AI application.

---

## 1. Virtual Environment Setup

The application is validated under **Python 3.12** inside the active virtual environment `backend\.venv`. 

### 1.1 Root dependencies (`requirements.txt`)
```text
# SignBridge AI dependencies
streamlit>=1.35.0
opencv-python>=4.8.0
mediapipe>=0.10.30
pymongo[srv]>=4.6.0
python-dotenv>=1.0.0
numpy>=1.24.0
pandas>=2.0.0
pytest>=8.0.0
httpx>=0.25.0
plotly>=5.18.0
gTTS>=2.4.0
```

### 1.2 Backend dependencies (`backend/requirements.txt`)
```text
fastapi>=0.115.0
uvicorn[standard]==0.24.0
pydantic[email]==2.9.1
pydantic-settings>=2.10.1,<3.0.0
motor==3.7.1
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
bcrypt==4.0.1
python-multipart==0.0.7
python-dotenv==1.0.0
mediapipe>=0.10.30
opencv-python
numpy
scikit-learn
pandas
pytest==8.3.2
httpx
```

---

## 2. Active Virtual Environment Freeze List (`pip freeze`)

The exact versions of packages currently installed and running the application in `backend\.venv` are listed below:

```text
absl-py==2.4.0
altair==6.2.1
annotated-doc==0.0.4
annotated-types==0.7.0
anyio==4.13.0
attrs==26.1.0
bcrypt==4.0.1
blinker==1.9.0
cachetools==7.1.4
certifi==2026.5.20
cffi==2.0.0
charset-normalizer==3.4.7
click==8.1.8
colorama==0.4.6
contourpy==1.3.3
cryptography==48.0.1
cycler==0.12.1
dnspython==2.8.0
ecdsa==0.19.2
email-validator==2.3.0
fastapi==0.111.1
fastapi-cli==0.0.24
filelock==3.29.3
flatbuffers==25.12.19
fonttools==4.63.0
fsspec==2026.4.0
gitdb==4.0.12
GitPython==3.1.50
gTTS==2.5.4
h11==0.16.0
httpcore==1.0.9
httptools==0.8.0
httpx==0.28.1
idna==3.18
iniconfig==2.3.0
itsdangerous==2.2.0
jax==0.10.1
jaxlib==0.10.1
Jinja2==3.1.6
joblib==1.5.3
jsonschema==4.26.0
jsonschema-specifications==2025.9.1
kiwisolver==1.5.0
markdown-it-py==4.2.0
MarkupSafe==3.0.3
matplotlib==3.10.9
mdurl==0.1.2
mediapipe==0.10.14
ml_dtypes==0.5.4
motor==3.7.1
mpmath==1.3.0
narwhals==2.22.1
networkx==3.6.1
numpy==2.4.6
opencv-contrib-python==4.13.0.92
opencv-python==4.13.0.92
opt_einsum==3.4.0
packaging==26.2
pandas==3.0.3
passlib==1.7.4
pillow==12.2.0
plotly==6.8.0
pluggy==1.6.0
protobuf==4.25.9
pyarrow==24.0.0
pyasn1==0.6.3
pycparser==3.0
pydantic==2.9.1
pydantic-settings==2.14.1
pydantic_core==2.23.3
pydeck==0.9.2
Pygments==2.20.0
pymongo==4.17.0
pyparsing==3.3.2
pytest==8.3.2
python-dateutil==2.9.0.post0
python-dotenv==1.0.0
python-jose==3.3.0
python-multipart==0.0.32
PyYAML==6.0.3
referencing==0.37.0
requests==2.34.2
rich==15.0.0
rich-toolkit==0.20.1
rpds-py==2026.5.1
rsa==4.9.1
scikit-learn==1.9.0
scipy==1.17.1
setuptools==81.0.0
shellingham==1.5.4
six==1.17.0
smmap==5.0.3
sounddevice==0.5.5
starlette==1.2.1
streamlit==1.58.0
sympy==1.14.0
tenacity==9.1.4
threadpoolctl==3.6.0
toml==0.10.2
torch==2.12.0
torchvision==0.27.0
typer==0.26.7
typing-inspection==0.4.2
typing_extensions==4.15.0
tzdata==2026.2
urllib3==2.7.0
uvicorn==0.49.0
watchdog==6.0.0
watchfiles==1.2.0
websockets==16.0
```

---

## 3. Version Compatibility Mappings & Critical Conflicts

For a successful rebuild, the following version combinations are required:

### 3.1 MediaPipe & Protobuf Compatibility
*   **Conflict**: MediaPipe heavily relies on underlying Protobuf specifications. In newer Python environments, installing default versions (`mediapipe 0.10.35+` with `protobuf 5.x+` or `7.x+`) removes internal modules, leading to the following error:
    `AttributeError: module 'mediapipe' has no attribute 'solutions'`
*   **Resolution**: Force-install the compatible pair:
    ```bash
    pip install mediapipe==0.10.14 protobuf==4.25.9
    ```

### 3.2 Deep Learning Framework (Torch & Torchvision)
*   **Conflict**: Running the model predictor without `torch` causes:
    `ModuleNotFoundError: No module named 'torch'`
*   **Resolution**: Install compatible CPU-wheel builds (standard on Windows dev machines) to avoid huge CUDA weight footprints:
    ```bash
    pip install torch==2.12.0 torchvision==0.27.0 --index-url https://download.pytorch.org/whl/cpu
    ```

### 3.3 Starlette & FastAPI
*   **Conflict**: FastAPIs `<0.115.0` are incompatible with Starlette versions `>0.38`.
*   **Resolution**: Keep `fastapi>=0.115.0` or lock the starlette library configuration to maintain runtime stability.
