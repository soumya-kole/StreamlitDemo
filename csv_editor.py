import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="CSV Editor", layout="wide")

st.title("📄 CSV File Editor")

# Upload CSV
uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    st.subheader("Edit the data below")
    edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)

    # Save modified CSV to buffer
    csv_buffer = io.StringIO()
    edited_df.to_csv(csv_buffer, index=False)
    csv_data = csv_buffer.getvalue()

    # Download button
    st.download_button(
        label="📥 Download Modified CSV",
        data=csv_data,
        file_name="modified.csv",
        mime="text/csv"
    )
