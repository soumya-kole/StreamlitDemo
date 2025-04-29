import streamlit as st
import pandas as pd
import snowflake.connector

# Snowflake connection parameters
SNOWFLAKE_USER = "soumyabrata"  # Replace with your username
SNOWFLAKE_PASSWORD = "***"  # Replace with your password
SNOWFLAKE_ACCOUNT = "***"  # Replace with your account identifier
SNOWFLAKE_WAREHOUSE = "COMPUTE_WH"  # Replace with your warehouse
SNOWFLAKE_DATABASE = "tasty_bytes_sample_data"  # Replace with your database
SNOWFLAKE_SCHEMA = "raw_pos"  # Replace with your schema


def execute_query(query):
    """Execute SQL query on Snowflake and return results as DataFrame"""
    try:
        # Create a connection to Snowflake
        conn = snowflake.connector.connect(
            user=SNOWFLAKE_USER,
            password=SNOWFLAKE_PASSWORD,
            account=SNOWFLAKE_ACCOUNT,
            warehouse=SNOWFLAKE_WAREHOUSE,
            database=SNOWFLAKE_DATABASE,
            schema=SNOWFLAKE_SCHEMA
        )

        # Execute query and fetch results
        cursor = conn.cursor()
        cursor.execute(query)

        # Get column names
        columns = [desc[0] for desc in cursor.description] if cursor.description else []

        # Fetch all results
        data = cursor.fetchall()

        # Close connection
        cursor.close()
        conn.close()

        # Return results as DataFrame
        if columns:
            return pd.DataFrame(data, columns=columns), None
        else:
            return None, f"Query executed successfully. Rows affected: {cursor.rowcount}"

    except Exception as e:
        return None, f"Error executing query: {str(e)}"


# Set page title
st.set_page_config(page_title="Snowflake Query Tool", page_icon="❄️")

# App title
st.title("Snowflake Query Tool ❄️")

# SQL query input
st.markdown("### Enter SQL Query")
query = st.text_area("", height=150, placeholder="SELECT * FROM your_table LIMIT 10")

# Execute button
if st.button("Execute Query", type="primary"):
    if query:
        # Show spinner while executing query
        with st.spinner("Executing query..."):
            df_result, message = execute_query(query)

        # Display results or message
        st.markdown("### Query Results")
        if df_result is not None:
            st.dataframe(df_result, use_container_width=True)
            st.success(f"Query returned {len(df_result)} rows")
        elif message:
            st.info(message)
    else:
        st.warning("Please enter a SQL query")