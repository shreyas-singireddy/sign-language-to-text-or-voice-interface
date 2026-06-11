# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-06-11

### Added
*   Added an interactive **Visual Debug Cockpit** Streamlit page to track annotated skeletons and joint coordinates.
*   Added comprehensive configuration profiles for ruff, mypy, pytest, and vulture inside `pyproject.toml`.
*   Added an automated validation verification script `validate_compliance.py`.
*   Added `.editorconfig`, `.env.example`, and `.dockerignore`.
*   Added `.pre-commit-config.yaml` to enforce formatting and lints locally.
*   Added `.gitlab-ci.yml` supporting multi-stage builds and auditing gates.

### Fixed
*   Fixed a critical coordinates overlap bug inside `perception_service.py` by shifting hand coordinate indices to non-overlapping boundaries (`1536` to `1662`).
*   Fixed `extractor.py` and `landmark_features.py` indexes to match the new coordinates offsets.
*   Fixed head rotation calculations in `face_detector.py` using a Perspective-n-Point (PnP) solver.
*   Fixed FastAPI/Starlette version clashes by upgrading dependencies in `requirements.txt`.
