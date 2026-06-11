# Conventional Commits Guidelines

All commit messages in this repository must follow the **Conventional Commits 1.0.0** specification. This enables automated changelog generation via `git-cliff` and enforces clean git history.

---

## 📐 Commit Message Structure

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

---

## 🏷️ Acceptable Commit Types

- `feat`: A new feature or capability.
- `fix`: A bug fix.
- `docs`: Documentation-only changes.
- `style`: Formatting, missing semi-colons, style guides (no code changes).
- `refactor`: Restructuring code without altering functional behavior.
- `perf`: Code modification specifically aimed at improving performance.
- `test`: Adding missing tests or correcting existing tests.
- `build`: Changes that affect the build system or external dependencies (pip, npm, docker).
- `ci`: Changes to CI/CD pipelines (GitLab CI, GitHub Actions).
- `chore`: Internal housekeeping, release tagging preparation.
- `security`: Security patches, vulnerability fixes, secret scanning.

---

## ✍️ Examples

### Simple Feature Commit
```
feat(perception): add dynamic hand gesture coordinate normalization
```

### Bug Fix with Scope & Description
```
fix(auth): prevent token signature expiration bypass in JWT middleware
```

### Breaking Change (indicated with `!`)
```
feat(api)!: remove deprecated v1 legacy translation socket endpoint
```
