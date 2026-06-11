# Contributing to SignBridge AI

Thank you for your interest in contributing to SignBridge AI! To maintain system integrity, code quality, and strict compliance metrics, all contributors must adhere to the workflows, code quality guidelines, and testing requirements outlined in this document.

---

## 📜 Code of Conduct

Please review and adhere to our [Code of Conduct](file:///CODE_OF_CONDUCT.md) before participating in this community. We expect a welcoming, inclusive, and professional environment for everyone.

---

## 🛠️ Development Setup

Refer to the [README.md](file:///README.md) for basic installation and dependencies. Ensure you install all development requirements inside `requirements-dev.txt`:

```bash
pip install -r requirements-dev.txt
```

---

## 🔄 Development Workflow

### 1. Branching Strategy
- **`main`**: The stable branch. Contains releases and verified builds.
- **`develop`**: The integration branch for new features.
- **`feature/<name>`**: Feature branches. Created from `develop`.
- **`bugfix/<name>`**: Bugfix branches. Created from `develop` or `main`.

### 2. Conventional Commit Guidelines
We enforce the **Conventional Commits** specification. The commit message must follow this structure:

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

#### Allowed Types:
- `feat`: A new feature.
- `fix`: A bug fix.
- `docs`: Documentation-only changes.
- `style`: Changes that do not affect the meaning of the code (white-space, formatting, missing semi-colons, etc.).
- `refactor`: A code change that neither fixes a bug nor adds a feature.
- `perf`: A code change that improves performance.
- `test`: Adding missing tests or correcting existing tests.
- `build`: Changes that affect the build system or external dependencies (example scopes: pip, npm).
- `ci`: Changes to our CI configuration files and scripts.
- `chore`: Other changes that do not modify src or test files.

#### Examples:
- `feat(perception): integrate multi-hand gesture recognition models`
- `fix(auth): resolve jwt expiration check validation bypass`
- `docs(api): add schema definition for /api/translate endpoint`

---

## 🧼 Code Quality Gates

Before pushing any commit, you must run the following validation suite. Code that fails any of these tools will be rejected by the CI/CD pipeline:

### 1. Linting & Style (Ruff)
We use `ruff` for fast linting and formatting. Run:
```bash
ruff check .
```

### 2. Static Type Checking (Mypy)
We enforce type hints across the backend. Run:
```bash
mypy .
```

### 3. Security Analysis (Bandit & Semgrep)
To verify that the code does not introduce security vulnerabilities or common pitfalls:
```bash
bandit -r .
semgrep scan .
```

### 4. Dead-Code Detection (Vulture)
To keep the codebase clean and maintainable:
```bash
vulture .
```

---

## 🧪 Testing Guidelines

We use `pytest` as our testing framework.
- All new features must be accompanied by unit or integration tests under the `tests/` directory.
- We require a minimum of **80% code coverage** for all modules.
- Run tests and generate coverage reports using:
  ```bash
  pytest --cov
  ```

---

## 🚀 Release Process & Git Tags

When releasing a new version:
1. Ensure all CI checks pass on the `develop` branch.
2. Merge `develop` into `main`.
3. Create a annotated git tag matching semantic versioning (e.g. `v1.0.0`):
   ```bash
   git tag -a v1.0.0 -m "Release version 1.0.0"
   ```
4. Push tags to the remote repository:
   ```bash
   git push origin v1.0.0
   ```
