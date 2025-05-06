import streamlit as st
import pandas as pd
import psycopg2
from datetime import datetime

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
def load_employee_table():
    df = pd.read_sql("SELECT * FROM hr.employee ORDER BY emp_id", conn)
    df["changed_by"] = df["changed_by"].fillna("")
    df["reason"] = df["reason"].fillna("")
    return df


# --- Initialize session state ---
if "data_initialized" not in st.session_state:
    st.session_state.data_initialized = False

if "message" not in st.session_state:
    st.session_state.message = None
    st.session_state.message_type = None


# --- Callback for commit button ---
def commit_changes():
    try:
        # Get current data from editor
        edited_data = st.session_state.employee_editor

        # Convert edited data to a proper DataFrame if needed
        if isinstance(edited_data, dict):
            # First, check if we got a dict of rows
            rows_list = []
            for row_key, row_data in edited_data.items():
                if isinstance(row_data, dict):
                    # Make sure to include the index (emp_id) in the row data
                    row_data_copy = row_data.copy()
                    if "emp_id" not in row_data_copy and row_key != "index":
                        try:
                            row_data_copy["emp_id"] = int(row_key)
                        except:
                            pass
                    rows_list.append(row_data_copy)
                else:
                    # This might be a dict of columns, not rows
                    # We'll handle this case in the except block
                    raise ValueError("Dict format not as expected")

            edited_df = pd.DataFrame(rows_list)
        else:
            edited_df = edited_data

        # Load original data for comparison
        original_df = st.session_state.original_data

        # Ensure both dataframes have 'emp_id' column
        if "emp_id" not in edited_df.columns or "emp_id" not in original_df.columns:
            st.error("Missing emp_id column. Cannot process changes.")
            return

        # Create copies with emp_id as index for comparison
        original_indexed = original_df.set_index("emp_id")
        edited_indexed = edited_df.set_index("emp_id")

        changes = []
        for emp_id in edited_indexed.index:
            if emp_id in original_indexed.index:  # Make sure the record exists
                edited_row = edited_indexed.loc[emp_id]
                original_row = original_indexed.loc[emp_id]

                # Check if all required columns exist
                required_columns = ["salary", "designation", "changed_by", "reason"]
                if not all(col in edited_row.index for col in required_columns) or \
                        not all(col in original_row.index for col in required_columns):
                    continue

                # Check all editable fields
                if not original_row[required_columns].equals(edited_row[required_columns]):
                    changes.append((
                        edited_row["salary"],
                        edited_row["designation"],
                        edited_row["changed_by"],
                        edited_row["reason"],
                        datetime.now(),
                        emp_id
                    ))

        # Update database if changes exist
        if changes:
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

            # Update message and refresh data
            st.session_state.message = f"{len(changes)} record(s) updated."
            st.session_state.message_type = "success"

            # Update the original data to reflect the new state
            st.session_state.original_data = load_employee_table()
            st.session_state.data_initialized = True
        else:
            st.session_state.message = "No changes detected."
            st.session_state.message_type = "info"

    except Exception as e:
        st.session_state.message = f"Error processing changes: {str(e)}"
        st.session_state.message_type = "error"


# --- UI ---
st.title("🧑‍💼 Employee Table Editor with Audit Fields")
st.caption("Editable: salary, designation, changed_by, reason")

# Display any messages
if st.session_state.message:
    if st.session_state.message_type == "success":
        st.success(st.session_state.message)
    elif st.session_state.message_type == "info":
        st.info(st.session_state.message)
    elif st.session_state.message_type == "error":
        st.error(st.session_state.message)
    # Clear message after displaying
    st.session_state.message = None
    st.session_state.message_type = None

# --- Load data only once, or after a commit ---
if not st.session_state.data_initialized:
    data = load_employee_table()
    st.session_state.original_data = data.copy()
    st.session_state.data_initialized = True
else:
    data = st.session_state.original_data.copy()

# --- Show editable table ---
reason_options = ["Promotion", "Correction", "Annual Review", "Other"]
st.data_editor(
    data,
    disabled=[col for col in data.columns if col not in ["salary", "designation", "changed_by", "reason"]],
    column_config={
        "reason": st.column_config.SelectboxColumn("Reason", options=reason_options),
    },
    use_container_width=True,
    num_rows="fixed",
    key="employee_editor"
)

# --- Commit button ---
st.button("💾 Commit Changes", on_click=commit_changes)