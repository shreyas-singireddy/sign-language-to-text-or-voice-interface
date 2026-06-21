#!/usr/bin/env python3
"""
scripts/deployment_check.py
============================
Pre-deployment validation script for SignBridge AI.

Exit codes:
  0 - All critical checks passed
  1 - One or more critical dependency failures
"""

import importlib
import sys

CRITICAL = []  # Must pass for app to start
OPTIONAL = []  # Nice-to-have; warns but does not fail


def check(package: str, critical: bool = True) -> bool:
    try:
        mod = importlib.import_module(package)
        version = getattr(mod, "__version__", "unknown")
        print(f"  [PASS]  {package} == {version}")
        return True
    except Exception as e:
        level = "FAIL" if critical else "WARN"
        print(f"  [{level}]  {package} — {e}")
        return False


print("\n=== SignBridge AI — Deployment Validation ===\n")

print("[ Critical dependencies ]")
CRITICAL.append(check("streamlit"))
CRITICAL.append(check("pydantic"))
CRITICAL.append(check("numpy"))
CRITICAL.append(check("pandas"))
CRITICAL.append(check("plotly"))
CRITICAL.append(check("pymongo"))
CRITICAL.append(check("gtts"))
CRITICAL.append(check("httpx"))

print("\n[ Vision dependencies (optional in cloud) ]")
OPTIONAL.append(check("cv2", critical=False))
OPTIONAL.append(check("mediapipe", critical=False))

print("\n[ Internal modules ]")
CRITICAL.append(check("config.config"))
CRITICAL.append(check("ai_engine.utils.dependency_guard"))
CRITICAL.append(check("conversation.schemas"))
CRITICAL.append(check("speech.schemas"))

print()

failed_critical = CRITICAL.count(False)
failed_optional = OPTIONAL.count(False)

if failed_critical:
    print(f"DEPLOYMENT CHECK FAILED — {failed_critical} critical dependency(ies) missing.")
    sys.exit(1)
else:
    if failed_optional:
        print(
            f"DEPLOYMENT CHECK PASSED (with {failed_optional} optional dep(s) missing — "
            "vision pages will degrade gracefully)."
        )
    else:
        print("DEPLOYMENT CHECK PASSED — All dependencies available.")
    sys.exit(0)
