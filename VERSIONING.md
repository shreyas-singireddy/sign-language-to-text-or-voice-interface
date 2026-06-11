# SignBridge AI Versioning Policy

We adhere to the **Semantic Versioning 2.0.0** (SemVer) standard for all releases of SignBridge AI.

---

## 🔢 Version Format

Our version numbers follow the standard:
```
MAJOR.MINOR.PATCH
```

1. **MAJOR version** (e.g. `v1.0.0`): incremented when you make incompatible API changes or significant architectural overhauls.
2. **MINOR version** (e.g. `v1.1.0`): incremented when you add functionality in a backwards compatible manner.
3. **PATCH version** (e.g. `v1.0.1`): incremented when you make backwards compatible bug fixes.

---

## 🏷️ Release Tagging Procedure

1. **Local Tagging**:
   Every release must have an annotated git tag matching the semantic version (prefixed with `v`):
   ```bash
   git tag -a v1.0.0 -m "Release version 1.0.0"
   ```
2. **Remote Tag Synchronization**:
   Push the tag to the remote repository:
   ```bash
   git push origin v1.0.0
   ```
3. **Automated Changelogs**:
   Ensure `git cliff` generates the corresponding release notes inside `CHANGELOG.md`.
