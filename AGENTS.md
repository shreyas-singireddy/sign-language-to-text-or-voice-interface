# Agent Instructions: Working on SignBridge AI

Welcome, agent! This document contains instructions to help you understand, modify, test, and validate the SignBridge AI codebase. Adhere to these constraints to ensure compliance checks remain green.

---

## 🗺️ Codebase Overview

```
├── .specify/                  # System specs & architecture blueprints
├── accessibility/             # Accessibility & theme manager modules
├── ai_engine/                 # Computer vision & deep learning models
│   ├── gesture_recognition/   # Gesture classifiers, inference engines, dataset utilities
│   └── services/              # Perception services interfacing MediaPipe
├── analytics/                 # User behavior analytics & metrics calculators
├── api_audit.md               # API endpoint audit logs
├── app/                       # Streamlit developer console application
├── assets/                    # Image mockups & UI visual assets
├── backend/                   # FastAPI backend implementation
│   ├── app/                   # FastAPI server codebase, auth, history controllers
│   └── .venv/                 # Python 3.12 virtualenv
├── communication/             # PubSub, communication hubs, and event buses
├── config/                    # Configuration loaders and YAML readers
├── database/                  # Database connections and Mongo client pools
├── frontend/                  # React + Vite + Tailwind UI frontend application
└── tests/                     # Test suite containing system and unit tests
```

---

## 🛠️ Code Modification Rules

### 1. Maintain Documentation Integrity
- Do **not** remove or modify existing comments, docstrings, or architectural writeups unless explicitly asked by the user.
- If you add or modify a module, update the corresponding file in `.specify/specs/` to prevent specifications from becoming stale.

### 2. Dependency Management
- Lock python packages in `requirements.txt` (core) and `requirements-dev.txt` (dev/compliance tools).
- Never introduce wildcard versions. Always pin using exact versions (e.g. `package==1.0.0`).
- Ensure `mediapipe==0.10.14` and `protobuf==4.25.9` are never modified or upgraded independently, as it causes protobuf deserialization errors.

---

## 🧼 Code Quality & Compliance Gates

Before ending your turn or claiming success, you must run and pass the following quality verification commands:

```bash
# 1. Formatting and lint checking
ruff check .

# 2. Strict static type analysis
mypy .

# 3. Security audits
bandit -r .

# 4. Dead-code inspection
vulture .

# 5. Run tests with coverage threshold checking
pytest --cov
```

All commands must complete with a **zero (0) exit status**. Warning files or TODO markers in tests are treated as failures.

---

## 📊 Spec-Kit Architecture

This repository uses a formal spec-kit configuration under `.specify/`.
- Every major feature block has a specification markdown under `.specify/specs/`.
- All design files must conform to the `.specify/constitution.md` design tokens.
- Maintain the specification mapping layout. If adding a new component, create its spec following `.specify/templates/spec_template.md`.
