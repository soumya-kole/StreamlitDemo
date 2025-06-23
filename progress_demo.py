import streamlit as st
import time

# Simulated backend logic
def do_something(): time.sleep(0.5)
def process_data(): time.sleep(0.5); return "processed"
def validate(x): time.sleep(10); return f"{x}_validated"

st.set_page_config(layout="centered")
st.title("🔧 Backend Step Progress with Status")

if st.button("🚀 Run Process"):
    progress_bar = st.progress(0)
    log_area = st.empty()
    logs = []

    total_steps = 3
    step = 0  # No nonlocal needed

    def log_step(message):
        logs.append(f"{message}...")
        log_area.code("\n".join(logs))

    def mark_done():
        logs[-1] = logs[-1].replace("...", "... Done")
        log_area.code("\n".join(logs))

    def advance_progress():
        nonlocal_step = len(logs)  # use length instead of tracking step separately
        progress_bar.progress(nonlocal_step / total_steps)

    # Step 1
    log_step("Loading data")
    do_something()
    mark_done()
    advance_progress()

    # Step 2
    log_step("Processing data")
    result = process_data()
    mark_done()
    advance_progress()

    # Step 3
    log_step("Validating results")
    validated = validate(result)
    mark_done()
    advance_progress()

    st.success("🎉 All steps completed!")
    # st.code(validated)
