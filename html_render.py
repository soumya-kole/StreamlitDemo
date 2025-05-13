import streamlit as st
import pandas as pd
from jinja2 import Template

# Sample data
df = pd.DataFrame({
    "Name": ["Charlie", "Soumya"],
    "Salary": [170000, 500000],
    "Designation": ["Director", "Sr Principal Engineer"]
})

# Jinja2 template with conditional coloring
html_template = """
<style>
    .low-salary { color: red; }
    .mid-salary { color: orange; }
    .high-salary { color: green; }
    table, th, td {
        border: 1px solid gray;
        border-collapse: collapse;
        padding: 8px;
    }
</style>

<table>
    <thead>
        <tr>
            {% for col in df.columns %}
                <th>{{ col }}</th>
            {% endfor %}
        </tr>
    </thead>
    <tbody>
        {% for row in df.itertuples(index=False) %}
            <tr>
                <td>{{ row.Name }}</td>
                <td class="{% if row.Salary < 100000 %}low-salary{% elif row.Salary <= 150000 %}mid-salary{% else %}high-salary{% endif %}">{{ row.Salary }}</td>
                <td>{{ row.Designation }}</td>
            </tr>
        {% endfor %}
    </tbody>
</table>
"""

# Render HTML using Jinja2
template = Template(html_template)
rendered_html = template.render(df=df)

# Fix: Use st.components.v1.html instead of st.markdown
import streamlit.components.v1 as components

dynamic_height = len(df) * 30 + 70
components.html(rendered_html, height=dynamic_height)

# Increase the height to ensure the bottom border is visible
# components.html(rendered_html, height=200)  # Adjusted from 150 to 180

# Alternative solution if st.write or components don't work as expected:
# from IPython.display import HTML
# import base64
# html_bytes = rendered_html.encode()
# encoded = base64.b64encode(html_bytes).decode()
# st.markdown(f'<iframe src="data:text/html;base64,{encoded}" width="100%" height="200" frameBorder="0"></iframe>', unsafe_allow_html=True)