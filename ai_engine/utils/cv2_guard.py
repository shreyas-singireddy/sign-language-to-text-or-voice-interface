"""
cv2_guard — backwards-compatible shim.
Delegates to dependency_guard so all existing imports continue to work.
"""
from ai_engine.utils.dependency_guard import (  # noqa: F401
    cv2,
    CV2_AVAILABLE,
    require_cv2,
    vision_unavailable_message,
)
