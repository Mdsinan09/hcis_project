import streamlit as st
# The import path must change to reflect the new location inside the 'src' folder
from src.pages import dashboard, report

# ----------------------------------------------------------------------
# Configuration to hide Streamlit's default page list (The "Crossbar")
# ----------------------------------------------------------------------
st.set_page_config(
    page_title="HCIS MVP",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Sidebar menu (Manual Navigation)
st.sidebar.title("HCIS Navigation")
# The st.radio creates the clean list: Dashboard or Report
page = st.sidebar.radio("Go to", ["Dashboard", "Report"])

# Page routing
if page == "Dashboard":
    # Call the show function from the dashboard module
    dashboard.show()
elif page == "Report":
    # Call the show function from the report module
    report.show()

# You can now delete the temporary 'pages/' folder from the root directory.
