import logging
import streamlit as st

try:
    import cv2
except ImportError as e:
    logging.error(f"OpenCV failed to initialize: {e}")
    cv2 = None

def require_cv2(func):
    """Decorator to disable functions requiring cv2 if it failed to load."""
    def wrapper(*args, **kwargs):
        if cv2 is None:
            st.error("Computer vision features are unavailable (missing system dependencies).")
            return None
        return func(*args, **kwargs)
    return wrapper
