import streamlit as st
import pandas as pd

# --- App pages ---
def show_home():
    st.title("📋 Welcome to the Multi-App Dashboard")
    st.write("Select an app from the sidebar or use the buttons below:")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("📄 Open CSV Editor"):
            st.session_state.page = "CSV Editor"
            st.rerun()

    with col2:
        if st.button("🧑‍💼 Open Employee Editor"):
            st.session_state.page = "Employee Editor"
            st.rerun()

def show_csv_editor():
    st.title("📄 CSV Editor")
    uploaded_file = st.file_uploader("Upload CSV", type="csv")
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        edited = st.data_editor(df, num_rows="dynamic", use_container_width=True)
        st.download_button("Download Modified CSV", edited.to_csv(index=False), "modified.csv", "text/csv")
    if st.button("🔙 Back to Home"):
        st.session_state.page = "Home"
        st.rerun()

def show_employee_editor():
    st.title("🧑‍💼 Employee Editor")
    st.write("This would connect to the employee DB (stub here).")
    st.success("Employee editor placeholder shown.")
    if st.button("🔙 Back to Home"):
        st.session_state.page = "Home"
        st.rerun()


# --- Define pages list in consistent format ---
PAGES = ["Home", "CSV Editor", "Employee Editor"]

# --- Initialize session state ---
if "page" not in st.session_state:
    st.session_state.page = "Home"

# --- Sidebar menu ---
st.sidebar.title("📂 App Menu")
selection = st.sidebar.radio("Navigate to", PAGES, index=PAGES.index(st.session_state.page))

# Update session state and rerun if selection changes
if selection != st.session_state.page:
    st.session_state.page = selection
    st.rerun()

# --- Render selected page ---
if st.session_state.page == "Home":
    show_home()
elif st.session_state.page == "CSV Editor":
    show_csv_editor()
elif st.session_state.page == "Employee Editor":
    show_employee_editor()
