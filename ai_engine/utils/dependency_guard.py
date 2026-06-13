"""
SignBridge AI — Dependency Guard
================================
Provides safe, graceful imports for all optional heavy dependencies.

All AI/vision modules must import from here instead of importing directly.
This ensures the Streamlit application NEVER crashes at startup due to a
missing library — instead it degrades gracefully per-page.

Usage:
    from ai_engine.utils.dependency_guard import cv2, CV2_AVAILABLE
    from ai_engine.utils.dependency_guard import mediapipe, MP_AVAILABLE

    if not CV2_AVAILABLE:
        st.warning("Camera features unavailable.")
        st.stop()
"""

import logging

logger = logging.getLogger("dependency_guard")

# ---------------------------------------------------------------------------
# OpenCV
# ---------------------------------------------------------------------------
try:
    import cv2  # noqa: F401 — re-exported
    CV2_AVAILABLE = True
    logger.debug("cv2 loaded successfully: %s", cv2.__version__)
except BaseException as _e:
    cv2 = None  # type: ignore[assignment]
    CV2_AVAILABLE = False
    logger.warning("cv2 unavailable (%s). Camera/vision features disabled.", _e)

# ---------------------------------------------------------------------------
# MediaPipe
# ---------------------------------------------------------------------------
try:
    import mediapipe as mp  # noqa: F401 — re-exported
    MP_AVAILABLE = True
    logger.debug("mediapipe loaded successfully.")
except BaseException as _e:
    mp = None  # type: ignore[assignment]
    MP_AVAILABLE = False
    logger.warning("mediapipe unavailable (%s). Holistic tracking disabled.", _e)

# ---------------------------------------------------------------------------
# PyTorch (optional — commented out in requirements.txt)
# ---------------------------------------------------------------------------
try:
    import torch  # noqa: F401 — re-exported
    TORCH_AVAILABLE = True
    logger.debug("torch loaded successfully: %s", torch.__version__)
except BaseException as _e:
    torch = None  # type: ignore[assignment]
    TORCH_AVAILABLE = False
    logger.info("torch unavailable (%s). Deep learning inference disabled.", _e)

# ---------------------------------------------------------------------------
# TensorFlow (optional — commented out in requirements.txt)
# ---------------------------------------------------------------------------
try:
    import tensorflow as tf  # noqa: F401 — re-exported
    TF_AVAILABLE = True
    logger.debug("tensorflow loaded successfully: %s", tf.__version__)
except BaseException as _e:
    tf = None  # type: ignore[assignment]
    TF_AVAILABLE = False
    logger.info("tensorflow unavailable (%s). TF inference disabled.", _e)

# ---------------------------------------------------------------------------
# Pydantic
# ---------------------------------------------------------------------------
try:
    import pydantic  # noqa: F401 — re-exported
    from pydantic import BaseModel, Field  # noqa: F401 — re-exported
    PYDANTIC_AVAILABLE = True
    logger.debug("pydantic loaded successfully: %s", pydantic.__version__)
except BaseException as _e:
    pydantic = None  # type: ignore[assignment]
    BaseModel = None  # type: ignore[assignment,misc]
    Field = None  # type: ignore[assignment]
    PYDANTIC_AVAILABLE = False
    logger.error("pydantic unavailable (%s). Schema validation disabled.", _e)


def vision_unavailable_message() -> None:
    """Display a graceful Streamlit warning when vision deps are missing."""
    try:
        import streamlit as st
        st.warning(
            "⚠️ **Computer Vision features are unavailable in this deployment.**\n\n"
            "This page requires OpenCV and/or MediaPipe, which could not be loaded "
            "in the current environment. All other pages remain fully functional.",
            icon="🚫",
        )
    except Exception:
        pass


def require_cv2() -> bool:
    """Returns True if cv2 is available, otherwise shows Streamlit warning and returns False."""
    if not CV2_AVAILABLE:
        vision_unavailable_message()
        return False
    return True


def require_mp() -> bool:
    """Returns True if mediapipe is available, otherwise shows Streamlit warning."""
    if not MP_AVAILABLE:
        vision_unavailable_message()
        return False
    return True


def require_torch() -> bool:
    """Returns True if torch is available, otherwise shows Streamlit warning."""
    if not TORCH_AVAILABLE:
        try:
            import streamlit as st
            st.warning(
                "⚠️ **Gesture Recognition is unavailable because PyTorch is not installed in this deployment.**\n\n"
                "To enable gesture translation models, PyTorch must be installed.",
                icon="🤖",
            )
        except Exception:
            pass
        return False
    return True
