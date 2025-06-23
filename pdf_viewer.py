import streamlit as st
import pdfplumber
import json
from PIL import Image
from io import BytesIO
import os

# --- Constants ---
PDF_FILE = "DistributionForm.pdf"
TEXT_JSON_FILE = "extracted_text.json"
STATUS_JSON_FILE = "page_status.json"

# --- Load Extracted Text ---
if os.path.exists(TEXT_JSON_FILE):
    with open(TEXT_JSON_FILE, "r") as f:
        page_text_list = json.load(f)
else:
    st.error("Missing extracted_text.json")
    st.stop()

# --- Load or Initialize Page Status Metadata ---
if os.path.exists(STATUS_JSON_FILE):
    with open(STATUS_JSON_FILE, "r") as f:
        page_status = json.load(f)
else:
    page_status = {}  # default to empty; treat as "review"

# --- Streamlit Setup ---
st.set_page_config(layout="wide")
st.title("📄 PDF Review App – Edit & Approve")

sidebar, content = st.columns([1, 5])

with pdfplumber.open(PDF_FILE) as pdf:
    num_pages = len(pdf.pages)
    page_numbers = list(range(1, num_pages + 1))

    # --- Page Selector (left) ---
    with sidebar:
        selected_page = st.radio(
            "Select Page",
            options=page_numbers,
            index=0,
            label_visibility="collapsed",
            format_func=lambda x: f"Page {x}"
        )

    # --- Data Preparation ---
    page_key = str(selected_page)
    page_dict = next((d for d in page_text_list if page_key in d), {page_key: ""})
    original_text = page_dict.get(page_key, "")
    current_status = page_status.get(page_key, "review")

    # --- Viewer & Editor (right) ---
    with content:
        img_col, text_col = st.columns(2)

        with img_col:
            page = pdf.pages[selected_page - 1]
            img = page.to_image(resolution=150)
            image_bytes = BytesIO()
            img.save(image_bytes, format="PNG")
            st.image(Image.open(BytesIO(image_bytes.getvalue())), caption=f"Page {selected_page}")

            # Status with refreshable placeholder
            status_placeholder = st.empty()
            status_placeholder.markdown(f"**Current Status:** `{current_status.upper()}`")

            # Approve button if not already approved
            if current_status != "approved":
                if st.button("✅ Approve Page"):
                    page_status[page_key] = "approved"
                    with open(STATUS_JSON_FILE, "w") as f:
                        json.dump(page_status, f, indent=2)
                    status_placeholder.markdown("**Current Status:** `APPROVED`")
                    st.success(f"Page {selected_page} marked as approved!")

        with text_col:
            st.subheader(f"Editable Text – Page {selected_page}")
            edited_text = st.text_area("Edit text if needed", value=original_text, height=600, key=f"edit_{selected_page}")

            if st.button("💾 Save Text Changes"):
                for d in page_text_list:
                    if page_key in d:
                        d[page_key] = edited_text
                        break
                else:
                    page_text_list.append({page_key: edited_text})
                with open(TEXT_JSON_FILE, "w") as f:
                    json.dump(page_text_list, f, indent=2)
                st.success(f"Saved updated text for page {selected_page}")
