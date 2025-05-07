import streamlit as st
import pandas as pd
import psycopg2
from datetime import datetime
import json

# --- DB Connection ---
DB_SETTINGS = {
    "host": "localhost",
    "port": 5432,
    "dbname": "mydb",
    "user": "admin",
    "password": "admin"
}


@st.cache_resource
def get_connection():
    return psycopg2.connect(**DB_SETTINGS)


conn = get_connection()
cursor = conn.cursor()


# --- Load employee table from DB ---
@st.cache_data(ttl=5)  # Cache for 5 seconds
def load_employee_table():
    df = pd.read_sql("SELECT * FROM hr.employee ORDER BY emp_id", conn)
    df["changed_by"] = df["changed_by"].fillna("")
    df["reason"] = df["reason"].fillna("")
    return df


# --- Initialize session state ---
if "edited_rows" not in st.session_state:
    st.session_state.edited_rows = {}

# --- UI ---
st.title("🧑‍💼 Employee Table Editor with Audit Fields")
st.caption("Editable: salary, designation, changed_by, reason")

# --- Load fresh data
data = load_employee_table()

# --- Show editable table ---
reason_options = ["Promotion", "Correction", "Annual Review", "Other"]
editor = st.data_editor(
    data,
    disabled=[col for col in data.columns if col not in ["salary", "designation", "changed_by", "reason"]],
    column_config={
        "reason": st.column_config.SelectboxColumn("Reason", options=reason_options),
    },
    use_container_width=True,
    num_rows="fixed",
    key="employee_editor",
    on_change=lambda: st.session_state.update({"edited_rows": st.session_state.employee_editor.get("edited_rows", {})})
)

# --- Get edited rows ---
edited_rows = st.session_state.employee_editor.get("edited_rows", {})

# --- Commit button ---
if st.button("💾 Commit Changes"):
    if edited_rows:
        changes = []

        # Process each edited row
        for row_idx, edited_values in edited_rows.items():
            # Get the emp_id from the data using the row index
            row_idx = int(row_idx)  # Convert string index to integer
            if row_idx < len(data):
                emp_id = int(data.iloc[row_idx]["emp_id"])  # Convert numpy.int64 to Python int

                # Only include columns that were actually edited
                salary = edited_values.get("salary", data.iloc[row_idx]["salary"])
                designation = edited_values.get("designation", data.iloc[row_idx]["designation"])
                changed_by = edited_values.get("changed_by", data.iloc[row_idx]["changed_by"])
                reason = edited_values.get("reason", data.iloc[row_idx]["reason"])

                # Convert NumPy types to Python native types
                if hasattr(salary, "item"):
                    salary = salary.item()
                if hasattr(designation, "item"):
                    designation = designation.item()
                if hasattr(changed_by, "item"):
                    changed_by = changed_by.item()
                if hasattr(reason, "item"):
                    reason = reason.item()

                changes.append((
                    salary,
                    designation,
                    changed_by,
                    reason,
                    datetime.now(),
                    emp_id
                ))

        # Apply changes to database
        for salary, designation, changed_by, reason, changed_time, emp_id in changes:
            cursor.execute("""
                UPDATE hr.employee
                SET salary = %s,
                    designation = %s,
                    changed_by = %s,
                    reason = %s,
                    changed_time = %s
                WHERE emp_id = %s
            """, (salary, designation, changed_by, reason, changed_time, emp_id))
        conn.commit()

        # Show success message
        st.success(f"{len(changes)} record(s) updated.")

        # Clear the edited_rows in session state
        st.session_state.edited_rows = {}

        # Force a refresh of the data (clear the cache)
        load_employee_table.clear()
        st.rerun()
    else:
        st.info("No changes detected.")

# --- Debug info (optional) ---
with st.expander("Debug Info"):
    st.write("Edited Rows:", edited_rows)