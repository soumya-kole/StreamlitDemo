import streamlit as st
import pandas as pd

# Sample DataFrame
df = pd.DataFrame({
    "Name": ["Alice", "Bob", "Charlie"],
    "Score": [85, 92, 78]
})

# Layout: Display DataFrame in the top container
with st.container():
    st.markdown("### 📋 Editable Data")
    st.dataframe(df, use_container_width=True)

# Spacer to push buttons lower
st.markdown("<br><br><br>", unsafe_allow_html=True)

# Layout: Buttons in bottom left and right
col1, col2, col3 = st.columns([1, 6, 1])  # Adjust ratios as needed

with col1:
    left_click = st.button("🔄 Reset")

with col3:
    right_click = st.button("💾 Save")

# Optional response to button click
if left_click:
    st.warning("Changes have been reset!")

if right_click:
    st.success("Changes saved successfully.")
