import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# Monkeypatch starlette to support both FastAPI 0.111.1 and Streamlit 1.58.0 requirements
try:
    import starlette.middleware.gzip
    if not hasattr(starlette.middleware.gzip, "DEFAULT_EXCLUDED_CONTENT_TYPES"):
        starlette.middleware.gzip.DEFAULT_EXCLUDED_CONTENT_TYPES = {
            "text/html",
            "text/css",
            "text/javascript",
            "application/javascript",
            "application/json",
            "application/xml",
        }
except ImportError:
    pass

import streamlit as st

from app.services.database_service import db_service
from config.config import PROJECT_NAME
from config.logger import setup_logger
from src.config.languages import SUPPORTED_LANGUAGES
from src.services.translation_service import get_direction_styles, t

logger = setup_logger("app.main")

# Initialize translation language setting in session state
if "language" not in st.session_state:
    st.session_state["language"] = "English"

# Set Page Config (Must be the very first Streamlit call)
st.set_page_config(
    page_title=f"{PROJECT_NAME} — accessibility first",
    page_icon="🤟",
    layout="wide",
    initial_sidebar_state="expanded",
)



# Global Bauhaus CSS Overrides
def inject_bauhaus_styles():
    st.markdown(
        """
        <style>
        /* Import Outfit & Space Grotesk */
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;800;900&family=Space+Grotesk:wght@500;700&display=swap');

        /* Base Overrides */
        html, body, .stApp {
            font-family: 'Outfit', sans-serif;
            background-color: #F0F0F0 !important;
            color: #121212 !important;
        }

        h1, h2, h3, h4, h5, h6 {
            font-family: 'Space Grotesk', sans-serif;
            text-transform: uppercase;
            font-weight: 900;
            color: #121212 !important;
        }

        /* Sidebar Styling */
        section[data-testid="stSidebar"] {
            background-color: #121212 !important;
            border-right: 5px solid #D02020 !important;
        }
        section[data-testid="stSidebar"] * {
            color: #F0F0F0 !important;
        }

        /* Bauhaus Containers (Constructivist Box) */
        .bauhaus-card {
            background-color: #FFFFFF !important;
            border: 3.5px solid #121212 !important;
            box-shadow: 8px 8px 0px #121212 !important;
            padding: 30px;
            margin-bottom: 25px;
            position: relative;
            transition: all 0.2s ease-in-out;
        }
        .bauhaus-card:hover {
            transform: translate(-3px, -3px);
            box-shadow: 11px 11px 0px #121212 !important;
        }

        .card-red {
            border-top: 15px solid #D02020 !important;
        }
        .card-blue {
            border-top: 15px solid #1040C0 !important;
        }
        .card-yellow {
            border-top: 15px solid #F0C020 !important;
        }

        /* Stark Buttons */
        .stButton>button {
            font-family: 'Space Grotesk', sans-serif !important;
            text-transform: uppercase !important;
            font-weight: 800 !important;
            font-size: 1.1rem !important;
            border: 3.5px solid #121212 !important;
            border-radius: 0px !important;
            box-shadow: 4px 4px 0px #121212 !important;
            background-color: #F0C020 !important;
            color: #121212 !important;
            transition: all 0.1s ease !important;
            padding: 12px 24px !important;
            width: 100% !important;
        }
        .stButton>button:hover {
            transform: translate(-2px, -2px) !important;
            box-shadow: 6px 6px 0px #121212 !important;
            background-color: #D02020 !important;
            color: #FFFFFF !important;
        }
        .stButton>button:active {
            transform: translate(2px, 2px) !important;
            box-shadow: 0px 0px 0px #121212 !important;
        }

        /* Custom Text Input override */
        div[data-testid="stTextInput"] input {
            border: 3px solid #121212 !important;
            border-radius: 0px !important;
            background-color: #FFFFFF !important;
            color: #121212 !important;
            font-size: 1.1rem !important;
            font-weight: 600 !important;
            padding: 10px !important;
        }

        /* Large Geometric Badges */
        .geo-number {
            font-family: 'Space Grotesk', sans-serif;
            font-size: 3.5rem;
            font-weight: 900;
            color: #FFFFFF;
            background-color: #121212;
            width: 70px;
            height: 70px;
            display: flex;
            align-items: center;
            justify-content: center;
            border: 3.5px solid #121212;
            margin-right: 15px;
            float: left;
        }

        .num-red { background-color: #D02020; }
        .num-blue { background-color: #1040C0; }
        .num-yellow { background-color: #F0C020; }

        /* Geometric Animations CSS */
        .geo-composition {
            position: relative;
            width: 100%;
            height: 250px;
            background-color: #E6E6E6;
            border: 3.5px solid #121212;
            overflow: hidden;
            margin-bottom: 20px;
        }

        .circle-shape {
            position: absolute;
            top: 50px;
            left: 50px;
            width: 120px;
            height: 120px;
            background-color: #1040C0;
            border-radius: 50%;
            border: 3.5px solid #121212;
            animation: pulse-circle 5s infinite ease-in-out alternate;
        }

        .square-shape {
            position: absolute;
            top: 80px;
            right: 60px;
            width: 100px;
            height: 100px;
            background-color: #F0C020;
            border: 3.5px solid #121212;
            animation: rotate-square 8s infinite linear;
        }

        .line-shape {
            position: absolute;
            bottom: 40px;
            left: 0;
            width: 100%;
            height: 15px;
            background-color: #D02020;
            border-top: 3.5px solid #121212;
            border-bottom: 3.5px solid #121212;
            transform: rotate(-15deg);
        }

        @keyframes pulse-circle {
            0% { transform: scale(1); }
            100% { transform: scale(1.2) translate(15px, 5px); }
        }

        @keyframes rotate-square {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        /* Custom layout structures */
        .flex-row {
            display: flex;
            align-items: center;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


inject_bauhaus_styles()

# Authentication Steps State Router
if "auth_step" not in st.session_state:
    st.session_state["auth_step"] = "splash"
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "user_name" not in st.session_state:
    st.session_state["user_name"] = ""
if "user_phone" not in st.session_state:
    st.session_state["user_phone"] = ""

# Browser Language Auto-Detection
if "detected_lang" not in st.session_state and "detected_lang" in st.query_params:
    detected_code = st.query_params["detected_lang"]
    base_code = detected_code.split('-')[0].lower()
    matched_lang = None
    for name, lang_meta in SUPPORTED_LANGUAGES.items():
        if lang_meta.code == base_code or lang_meta.bcp47.lower() == detected_code.lower():
            matched_lang = name
            break
    if matched_lang:
        st.session_state["language"] = matched_lang
        st.session_state["detected_lang"] = detected_code

# Non-blocking iframe bridge to extract navigator.language and update query param
if "detected_lang" not in st.session_state and "detected_lang" not in st.query_params:
    st.components.v1.html(
        """
        <script>
        const userLang = navigator.language || navigator.userLanguage;
        const parentUrlObj = new URL(window.parent.location.href);
        if (!parentUrlObj.searchParams.has('detected_lang')) {
            parentUrlObj.searchParams.set('detected_lang', userLang);
            window.parent.location.href = parentUrlObj.toString();
        }
        </script>
        """,
        height=0,
        width=0
    )

# Inject dynamic RTL stylesheet if language is RTL
dir_styles = get_direction_styles(st.session_state["language"])
if dir_styles["direction"] == "rtl":
    st.markdown(
        """
        <style>
        html, body, .stApp {
            direction: rtl;
            text-align: right;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

# Sidebar Global Language Selector
with st.sidebar:
    st.markdown(f"### {t('language_selector_label')}")
    lang_list = list(SUPPORTED_LANGUAGES.keys())
    current_lang = st.session_state.get("language", "English")
    if current_lang not in lang_list:
        current_lang = "English"
    lang_idx = lang_list.index(current_lang)

    selected_lang = st.selectbox(
        "SELECT LANGUAGE",
        options=lang_list,
        index=lang_idx,
        key="global_lang_selector",
        label_visibility="collapsed",
    )
    if selected_lang != current_lang:
        st.session_state["language"] = selected_lang
        # If authenticated, persist preference
        if st.session_state.get("authenticated") and st.session_state.get("user_phone"):
            db_service.save_user_language(st.session_state["user_phone"], selected_lang)
        st.rerun()


# Handle Login Flow
if not st.session_state["authenticated"]:
    # Grid margins for centering
    left_spacer, center_col, right_spacer = st.columns([1, 2, 1])

    with center_col:
        # 1. SPLASH SCREEN STEP
        if st.session_state["auth_step"] == "splash":
            st.html("<div style='height: 40px;'></div>")
            st.html(f"""
                <div class="bauhaus-card card-red" style="text-align: center;">
                    <h1 style="font-size: 3.5rem; letter-spacing: -2px; margin-bottom: 5px; color: #121212 !important;">{t("splash_title")}</h1>
                    <p style="font-size: 1.25rem; font-weight: 600; text-transform: uppercase; color: #1040C0 !important; margin-top: 0px;">
                        {t("splash_subtitle")}
                    </p>

                    <div class="geo-composition">
                        <div class="circle-shape"></div>
                        <div class="square-shape"></div>
                        <div class="line-shape"></div>
                    </div>

                    <p style="font-size: 1rem; color: #555555; margin-bottom: 25px;">
                        {t("splash_desc")}
                    </p>
                </div>
                """)

            if st.button(t("enter_button"), key="btn_enter_splash"):
                st.session_state["auth_step"] = "login"
                st.rerun()

        # 2. LOGIN FORM STEP
        elif st.session_state["auth_step"] == "login":
            st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)
            st.html(f"""
                <div class="bauhaus-card card-blue">
                    <h2 style="font-size: 2.2rem; margin-bottom: 10px; color: #121212 !important;">{t("register_title")}</h2>
                    <p style="font-size: 0.95rem; color: #555555; margin-bottom: 20px;">
                        {t("register_desc")}
                    </p>
                </div>
                """)

            with st.container(border=True):
                name = st.text_input(
                    t("full_name"),
                    placeholder=t("full_name_placeholder"),
                    key="input_login_name",
                )
                phone = st.text_input(
                    t("mobile_number"),
                    placeholder=t("mobile_number_placeholder"),
                    key="input_login_phone",
                )

                st.markdown("<br/>", unsafe_allow_html=True)

                if st.button(t("request_otp_button"), key="btn_req_otp"):
                    if name.strip() and phone.strip():
                        st.session_state["user_name"] = name
                        st.session_state["user_phone"] = phone
                        st.session_state["auth_step"] = "otp"
                        st.rerun()
                    else:
                        st.error(t("error_fill_fields"))

        # 3. OTP VERIFICATION STEP
        elif st.session_state["auth_step"] == "otp":
            st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)
            st.html(f"""
                <div class="bauhaus-card card-yellow">
                    <h2 style="font-size: 2.2rem; margin-bottom: 10px; color: #121212 !important;">{t("otp_title")}</h2>
                    <p style="font-size: 0.95rem; color: #555555; margin-bottom: 15px;">
                        {t("otp_desc", phone=st.session_state['user_phone'])}
                    </p>
                    <div style="background-color: #E6E6E6; border: 2px dashed #121212; padding: 10px; font-weight: bold; text-align: center; margin-bottom: 20px;">
                        {t("demo_otp")}: <span style="font-size: 1.25rem; color: #D02020;">1919</span>
                    </div>
                </div>
                """)

            with st.container(border=True):
                otp_code = st.text_input(
                    t("enter_otp"),
                    placeholder=t("enter_otp_placeholder"),
                    key="input_otp_code",
                )

                st.markdown("<br/>", unsafe_allow_html=True)
                col_sub1, col_sub2 = st.columns(2)
                with col_sub1:
                    if st.button(t("verify_otp_button"), key="btn_verify_otp"):
                        if otp_code.strip() == "1919":
                            st.session_state["auth_step"] = "welcome"
                            # Load language preference from DB upon login
                            saved_lang = db_service.get_user_language(st.session_state["user_phone"])
                            if saved_lang and saved_lang in SUPPORTED_LANGUAGES:
                                st.session_state["language"] = saved_lang
                            st.rerun()
                        else:
                            st.error(t("error_invalid_otp"))
                with col_sub2:
                    if st.button(t("back_button"), key="btn_back_otp"):
                        st.session_state["auth_step"] = "login"
                        st.rerun()

        # 4. WELCOME STEP
        elif st.session_state["auth_step"] == "welcome":
            st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)
            st.html(f"""
                <div class="bauhaus-card card-red" style="text-align: center;">
                    <h2 style="font-size: 2.5rem; margin-bottom: 10px; color: #121212 !important;">{t("welcome_title")}</h2>
                    <p style="font-size: 1.25rem; color: #1040C0; font-weight: bold; text-transform: uppercase;">
                        {st.session_state['user_name']}
                    </p>
                    <p style="font-size: 1rem; color: #555555; margin-bottom: 25px;">
                        {t("welcome_desc")}
                    </p>
                </div>
                """)

            if st.button(t("launch_button"), key="btn_launch_app"):
                st.session_state["authenticated"] = True
                st.session_state["auth_step"] = "dashboard"
                st.rerun()

    st.stop()  # Prevents other pages/sidebar navigation from loading!

# ----------------- REGULAR DASHBOARD OPERATION -----------------
# Page navigation setup
pages_dir = Path(__file__).resolve().parent / "pages"
frontend_pages_dir = Path(__file__).resolve().parent.parent / "frontend" / "pages"

# Define multipage navigation structure
pages = [
    st.Page(pages_dir / "home.py", title=t("sidebar_home"), icon="🏠"),
    st.Page(
        frontend_pages_dir / "live_vision_engine.py",
        title=t("sidebar_live_vision"),
        icon="👁️",
    ),
    st.Page(
        frontend_pages_dir / "live_gesture_recognition.py",
        title=t("sidebar_live_gesture"),
        icon="🤟",
    ),
    st.Page(
        pages_dir / "ai_agent_hub.py",
        title=t("sidebar_ai_agent_hub"),
        icon="🤖",
    ),
    st.Page(
        pages_dir / "computer_control.py",
        title="Computer Control Agent",
        icon="🖥️",
    ),
    st.Page(pages_dir / "visual_debug_dashboard.py", title=t("sidebar_visual_debug"), icon="🛠️"),
    st.Page(pages_dir / "live_translation.py", title=t("sidebar_live_translation"), icon="🎥"),
    st.Page(pages_dir / "training_studio.py", title=t("sidebar_training_studio"), icon="🏋️"),
    st.Page(pages_dir / "communication_hub.py", title=t("sidebar_conversation_hub"), icon="💬"),
    st.Page(pages_dir / "analytics.py", title=t("sidebar_analytics"), icon="📊"),
    st.Page(pages_dir / "accessibility.py", title=t("sidebar_accessibility"), icon="♿"),
    st.Page(pages_dir / "emergency.py", title=t("sidebar_emergency"), icon="🚨"),
    st.Page(pages_dir / "settings.py", title=t("sidebar_settings"), icon="⚙️"),
    st.Page(pages_dir / "admin.py", title=t("sidebar_admin"), icon="🛡️"),
]

# Run Multi-page Routing
pg = st.navigation(pages)
pg.run()
