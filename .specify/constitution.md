# Constitution of Specifications (Spec-Kit Constitution)

This document establishes the binding standards, governance, and format rules for all technical specifications in the SignBridge AI project. Every subsystem and feature must map to a corresponding specification in this kit.

---

## 🏛️ Governance Rules

1. **Source of Truth**: The specifications in this directory are the authoritative technical blueprints. Any discrepancy between implementation code and these specifications is considered a system defect.
2. **Component Lifecycle**:
   - **Proposed**: A new capability or architecture change under discussion.
   - **Active**: Approved specification currently implemented in the codebase.
   - **Deprecated**: Planned for removal in subsequent iterations.
3. **Traceability**: All functional blocks in the source code (e.g. classes, decorators, endpoints) must trace back to a specific requirement key defined in these documents.
4. **Spec-First Development**: New features MUST have a specification in `.specify/specs/` before implementation begins.

---

## 📂 Directory Layout

```
.specify/
├── constitution.md          ← This file (governance rules)
├── templates/
│   ├── spec_template.md     ← Minimal spec template
│   ├── feature-spec.md      ← Full feature specification template
│   ├── architecture-spec.md ← System architecture documentation template
│   └── task-spec.md         ← Implementation task template
└── specs/
    ├── hand_tracking.md
    ├── face_tracking.md
    ├── body_tracking.md
    ├── gesture_recognition.md
    ├── live_translation.md
    ├── speech_engine.md
    ├── telemetry_dashboard.md
    ├── translation_engine.md
    ├── database_service_spec.md
    └── feature-001/
        ├── spec.md          ← Feature specification
        ├── tasks.md         ← Task breakdown
        └── design.md        ← Technical design document
```

---

## 📐 Design & Quality Constraints

- **Modularity**: Specifications must define clean, decoupled boundaries between modules.
- **Verification Strategy**: Every specification must include a verification section defining how automated unit/integration tests validate the implementation.
- **Design Tokens**: Standard font mappings, UI color palettes, contrast settings, and telemetry formats must align with the global styling variables defined in [theme_manager.py](file:///accessibility/theme_manager.py) and Tailwind CSS configurations.
- **Security Gates**: System components that touch user input or sensitive profiles must define threat boundaries and input validation models.

---

## 🔧 Tooling Requirements

All specifications must be validated by these CI gates before merging:

| Gate | Tool | Config |
|------|------|--------|
| Lint | `ruff check .` | `pyproject.toml` |
| Format | `black --check .` | `pyproject.toml` |
| Type Check | `mypy .` | `pyproject.toml` |
| Security | `bandit -r .` | `.bandit` |
| Dead Code | `vulture .` | `pyproject.toml` |
| Python Syntax Upgrade | `pyupgrade --py312-plus` | `.pre-commit-config.yaml` |
| Dependency Audit | `pip-audit` | `requirements-dev.txt` |
| Node Audit | `npm audit` | `frontend/package.json` |
| Tests | `pytest --cov --cov-fail-under=80` | `pyproject.toml` |
| Compliance | `python validate_compliance.py` | `scripts/validate_compliance.py` |

---

## 📋 Spec Authoring Guide

1. Copy the appropriate template from `.specify/templates/`.
2. Fill in all required sections. Placeholder text is a failure.
3. Set **Status** to `Proposed` initially.
4. Submit via MR with the feature branch.
5. After code review and CI pass, update **Status** to `Active`.
6. When removing a feature, update **Status** to `Deprecated` and note the removal version.

---

## 🔗 Key References

- [feature-spec.md template](templates/feature-spec.md)
- [architecture-spec.md template](templates/architecture-spec.md)
- [task-spec.md template](templates/task-spec.md)
- [Feature 001 Spec](specs/feature-001/spec.md)
