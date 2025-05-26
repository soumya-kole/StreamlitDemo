import streamlit as st
import base64

def img_to_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

img_base64 = img_to_base64("home_button.jpeg")

st.markdown(f"""
    <a href="?clicked=true">
        <img src="data:image/png;base64,{img_base64}" alt="button" style="width:150px;">
    </a>
""", unsafe_allow_html=True)

if st.query_params.get("clicked"):
    st.success("You clicked the image!")
