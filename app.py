import streamlit as st
from pathlib import Path

# -------------------------------
# 1️⃣ Global CSS Loader
# -------------------------------
def load_css():
    css_path = Path(__file__).parent / "assets" / "style.css"
    if css_path.exists():
        with open(css_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# -------------------------------
# 2️⃣ Safe Import Helper
# -------------------------------
def safe_import(module_path, attr):
    """Safely import a UI component so that the app doesn't crash if there's an import error."""
    try:
        module = __import__(module_path, fromlist=[attr])
        return getattr(module, attr)
    except Exception as e:
        # Pass 'e' as a default argument to avoid closure issues
        def error_page(exc=e, mod=module_path, at=attr):
            st.error(f"❌ Failed to import `{mod}.{at}`")
            st.exception(exc)
        return error_page

# -------------------------------
# 3️⃣ Import UI Pages
# -------------------------------
dashboard_ui = safe_import("src.pages.dashboard", "dashboard_ui")
chatbot_ui = safe_import("src.pages.chatbot", "chatbot_ui")
deepfake_ui = safe_import("src.pages.deepfake", "deepfake_ui")
report_ui = safe_import("src.pages.report", "report_ui")

# -------------------------------
# 4️⃣ Streamlit Config + Load CSS
# -------------------------------
st.set_page_config(page_title="Holistic Content Integrity System", layout="wide", page_icon="🧠")
load_css()

# -------------------------------
# 5️⃣ Sidebar Navigation
# -------------------------------
with st.sidebar:
    st.title("🌐 Navigation")
    st.markdown("<hr>", unsafe_allow_html=True)
    page = st.radio("Choose a page:", [
        "🏠 Dashboard", 
        "💬 Chatbot", 
        "🧪 Deepfake Generator", 
        "📊 Report"
    ])

# -------------------------------
# 6️⃣ Page Routing
# -------------------------------
if page == "🏠 Dashboard":
    dashboard_ui()
elif page == "💬 Chatbot":
    chatbot_ui()
elif page == "🧪 Deepfake Generator":
    deepfake_ui()
elif page == "📊 Report":
    report_ui()
