# [Task Name] Task Specification

**Task ID:** TASK-XXX  
**Linked Feature:** FEAT-XXX  
**Status:** Todo | In Progress | In Review | Done  
**Assignee:** @username  
**Sprint:** Sprint-XX  
**Estimated Effort:** X story points  
**Last Updated:** YYYY-MM-DD

---

## 1. Summary

One-sentence description of what this task achieves.

## 2. Context & Motivation

Why is this task needed? What problem does it solve or what feature does it enable?

## 3. Acceptance Criteria

- [ ] Criterion 1: Clearly verifiable condition.
- [ ] Criterion 2: Observable behaviour or output.
- [ ] Criterion 3: Test or CI check that must pass.

## 4. Technical Approach

### Files to Modify
| File | Change |
|------|--------|
| `module/file.py` | Add/modify function `foo()` |
| `tests/test_file.py` | Add unit tests for `foo()` |

### Implementation Steps
1. Step 1: Describe the first action.
2. Step 2: Describe the second action.
3. Step 3: Commit with message: `feat(module): short description`.

### Edge Cases
- What happens if input is empty?
- What happens if the external dependency is unavailable?

## 5. Testing Requirements

| Test Type | Target | Command |
|-----------|--------|---------|
| Unit | `module.foo()` | `pytest tests/test_file.py` |
| Integration | API endpoint | `pytest tests/test_integration.py` |

## 6. Definition of Done

- [ ] All acceptance criteria met.
- [ ] Tests written and passing.
- [ ] `ruff check .` passes.
- [ ] `mypy .` passes.
- [ ] `bandit -r .` passes.
- [ ] `vulture .` passes.
- [ ] Coverage ≥ 80%.
- [ ] Code reviewed and approved.
- [ ] Spec updated if architectural decisions changed.

## 7. Dependencies & Blockers

- Blocked by: TASK-XXX (if applicable)
- Depends on: external library / API / environment variable

## 8. References

- [Feature Spec](../feature-001/spec.md)
- [Constitution](../../constitution.md)
