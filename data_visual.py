import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

# Set page config
st.set_page_config(page_title="CSV Analytics Dashboard", layout="wide")

# Custom CSS to improve appearance
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        margin-bottom: 1rem;
    }
    .section-header {
        margin-top: 1.5rem;
        margin-bottom: 0.8rem;
    }
    .stPlotlyChart {
        margin-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# App header
st.markdown("<h1 class='main-header'>📊 CSV Analytics Dashboard</h1>", unsafe_allow_html=True)
st.markdown("Upload your CSV file to visualize and analyze your data.")

# File uploader
uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

# Initialize empty dataframe
df = None

# Data processing
if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)
        st.success(f"Successfully loaded {uploaded_file.name}")
    except Exception as e:
        st.error(f"Error: {e}")

# Main analysis section
if df is not None:
    # Create tabs for different analyses
    tab1, tab2, tab3 = st.tabs(["📊 Overview", "📈 Visualizations", "🔍 Detailed Analysis"])

    with tab1:
        st.markdown("<h2 class='section-header'>Data Preview</h2>", unsafe_allow_html=True)

        # Add row count slider
        preview_rows = st.slider("Number of rows to preview", 1, min(50, df.shape[0]), 5)
        st.dataframe(df.head(preview_rows))

        # Data info in columns
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("<h3 class='section-header'>Dataset Information</h3>", unsafe_allow_html=True)
            st.write(f"**Rows:** {df.shape[0]}")
            st.write(f"**Columns:** {df.shape[1]}")

            # Missing values analysis
            st.markdown("<h3 class='section-header'>Missing Values</h3>", unsafe_allow_html=True)
            missing = df.isnull().sum()
            missing_percent = (missing / len(df)) * 100
            missing_df = pd.DataFrame({
                'Missing Values': missing,
                'Percentage (%)': missing_percent.round(2)
            })
            st.dataframe(missing_df[missing_df['Missing Values'] > 0].sort_values(by='Missing Values', ascending=False))

        with col2:
            st.markdown("<h3 class='section-header'>Column Types</h3>", unsafe_allow_html=True)
            types_df = pd.DataFrame({
                'Column': df.columns,
                'Type': df.dtypes.astype(str),
                'Unique Values': [df[col].nunique() for col in df.columns]
            })
            st.dataframe(types_df)

        # Summary statistics
        st.markdown("<h3 class='section-header'>Summary Statistics</h3>", unsafe_allow_html=True)

        # Let user choose columns for summary
        all_cols = st.checkbox("Show all columns", value=True)
        if all_cols:
            selected_cols = df.columns.tolist()
        else:
            selected_cols = st.multiselect("Select columns for summary", df.columns.tolist(),
                                           default=df.select_dtypes(include=['number']).columns.tolist()[:5])

        if selected_cols:
            st.dataframe(df[selected_cols].describe(include='all').T)

    with tab2:
        st.markdown("<h2 class='section-header'>Data Visualization</h2>", unsafe_allow_html=True)

        # Identify column types
        num_cols = df.select_dtypes(include=['float64', 'int64']).columns.tolist()
        cat_cols = df.select_dtypes(include=['object', 'category', 'bool']).columns.tolist()
        date_cols = [col for col in df.columns if df[col].dtype == 'datetime64[ns]' or
                     (df[col].dtype == 'object' and pd.to_datetime(df[col], errors='coerce').notna().all())]

        viz_type = st.selectbox("Select Visualization Type",
                                ["Histogram", "Scatter Plot", "Bar Chart", "Box Plot",
                                 "Correlation Heatmap", "Pair Plot"])

        if viz_type == "Histogram" and num_cols:
            col = st.selectbox("Select column for histogram", num_cols)
            bins = st.slider("Number of bins", 5, 100, 20)

            fig, ax = plt.subplots(figsize=(10, 6))
            sns.histplot(df[col].dropna(), kde=True, bins=bins, ax=ax)
            ax.set_title(f'Histogram of {col}')
            ax.set_xlabel(col)
            ax.set_ylabel('Frequency')
            st.pyplot(fig)

        elif viz_type == "Scatter Plot" and len(num_cols) >= 2:
            col1, col2 = st.columns(2)
            with col1:
                x_col = st.selectbox("X-axis for scatterplot", num_cols)
            with col2:
                y_col = st.selectbox("Y-axis for scatterplot", [c for c in num_cols if c != x_col])

            color_option = None
            if cat_cols:
                use_color = st.checkbox("Color by category", value=False)
                if use_color:
                    color_option = st.selectbox("Select category for color", cat_cols)

            fig, ax = plt.subplots(figsize=(10, 6))
            if color_option:
                sns.scatterplot(data=df, x=x_col, y=y_col, hue=color_option, ax=ax)
                plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
            else:
                sns.scatterplot(data=df, x=x_col, y=y_col, ax=ax)

            ax.set_title(f'{y_col} vs {x_col}')
            plt.tight_layout()
            st.pyplot(fig)

        elif viz_type == "Bar Chart" and cat_cols:
            cat_col = st.selectbox("Select categorical column", cat_cols)

            # Option for count or aggregating by a numeric column
            agg_option = st.radio("Select aggregation", ["Count", "Mean of numeric column", "Sum of numeric column"])

            fig, ax = plt.subplots(figsize=(10, 6))

            if agg_option == "Count":
                value_counts = df[cat_col].value_counts().sort_values(ascending=False)

                # Limit categories if there are too many
                if len(value_counts) > 15:
                    st.warning(f"Showing only top 15 categories out of {len(value_counts)}")
                    value_counts = value_counts.head(15)

                value_counts.plot(kind='bar', ax=ax)
                ax.set_title(f'Count of {cat_col}')
                ax.set_ylabel('Count')
            else:
                if num_cols:
                    num_col = st.selectbox("Select numeric column", num_cols)

                    if agg_option == "Mean of numeric column":
                        agg_df = df.groupby(cat_col)[num_col].mean().sort_values(ascending=False)
                        title = f'Mean {num_col} by {cat_col}'
                        ylabel = f'Mean {num_col}'
                    else:  # Sum
                        agg_df = df.groupby(cat_col)[num_col].sum().sort_values(ascending=False)
                        title = f'Sum of {num_col} by {cat_col}'
                        ylabel = f'Sum of {num_col}'

                    # Limit categories if there are too many
                    if len(agg_df) > 15:
                        st.warning(f"Showing only top 15 categories out of {len(agg_df)}")
                        agg_df = agg_df.head(15)

                    agg_df.plot(kind='bar', ax=ax)
                    ax.set_title(title)
                    ax.set_ylabel(ylabel)
                else:
                    st.warning("No numeric columns available for aggregation")

            plt.tight_layout()
            st.pyplot(fig)

        elif viz_type == "Box Plot":
            if num_cols:
                num_col = st.selectbox("Select numeric column for box plot", num_cols)

                group_by = None
                if cat_cols:
                    use_grouping = st.checkbox("Group by category", value=False)
                    if use_grouping:
                        group_by = st.selectbox("Select category for grouping", cat_cols)

                fig, ax = plt.subplots(figsize=(10, 6))

                if group_by:
                    # Limit categories if there are too many
                    categories = df[group_by].unique()
                    if len(categories) > 10:
                        st.warning(f"Too many categories ({len(categories)}). Showing only top 10 by frequency.")
                        top_cats = df[group_by].value_counts().nlargest(10).index.tolist()
                        plot_df = df[df[group_by].isin(top_cats)]
                    else:
                        plot_df = df

                    sns.boxplot(x=group_by, y=num_col, data=plot_df, ax=ax)
                    plt.xticks(rotation=45)
                    ax.set_title(f'Box Plot of {num_col} by {group_by}')
                else:
                    sns.boxplot(y=df[num_col], ax=ax)
                    ax.set_title(f'Box Plot of {num_col}')

                plt.tight_layout()
                st.pyplot(fig)
            else:
                st.warning("No numeric columns available for box plot")

        elif viz_type == "Correlation Heatmap" and len(num_cols) >= 2:
            # Allow user to select columns for correlation
            corr_cols = st.multiselect("Select columns for correlation matrix", num_cols,
                                       default=num_cols[:min(len(num_cols), 8)])

            if corr_cols and len(corr_cols) >= 2:
                fig, ax = plt.subplots(figsize=(10, 8))
                corr_matrix = df[corr_cols].corr()
                mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
                sns.heatmap(corr_matrix, mask=mask, annot=True, cmap='coolwarm',
                            linewidths=0.5, ax=ax, fmt=".2f", annot_kws={"size": 8})
                plt.tight_layout()
                st.pyplot(fig)
            else:
                st.warning("Please select at least 2 columns for correlation matrix")

        elif viz_type == "Pair Plot" and len(num_cols) >= 2:
            # Allow user to select a subset of columns
            pair_cols = st.multiselect("Select columns for pair plot", num_cols,
                                       default=num_cols[:min(len(num_cols), 4)])

            hue_col = None
            if cat_cols:
                use_hue = st.checkbox("Color by category", value=False)
                if use_hue:
                    hue_col = st.selectbox("Select category for color", cat_cols)

            if pair_cols and len(pair_cols) >= 2:
                if len(pair_cols) > 4:
                    st.warning("Using many columns in pair plot may slow down the dashboard")

                with st.spinner("Generating pair plot..."):
                    if hue_col:
                        # Limit categories if there are too many
                        if df[hue_col].nunique() > 5:
                            st.warning(f"Too many categories in {hue_col}. Using only top 5 categories.")
                            top_cats = df[hue_col].value_counts().nlargest(5).index.tolist()
                            plot_df = df[df[hue_col].isin(top_cats)]
                        else:
                            plot_df = df

                        fig = sns.pairplot(plot_df, vars=pair_cols, hue=hue_col, height=2.5)
                    else:
                        fig = sns.pairplot(df, vars=pair_cols, height=2.5)

                    plt.tight_layout()
                    st.pyplot(fig)
            else:
                st.warning("Please select at least 2 columns for pair plot")

    with tab3:
        st.markdown("<h2 class='section-header'>Detailed Analysis</h2>", unsafe_allow_html=True)

        # Add column filter
        st.markdown("<h3 class='section-header'>Column Analysis</h3>", unsafe_allow_html=True)
        selected_col = st.selectbox("Select column to analyze", df.columns.tolist())

        col1, col2 = st.columns(2)

        with col1:
            # Basic column stats
            st.markdown(f"**Basic Statistics for {selected_col}**")
            if df[selected_col].dtype in ['int64', 'float64']:
                stats = pd.DataFrame({
                    'Statistic': ['Mean', 'Median', 'Std Dev', 'Min', 'Max', 'Range'],
                    'Value': [
                        round(df[selected_col].mean(), 2),
                        round(df[selected_col].median(), 2),
                        round(df[selected_col].std(), 2),
                        round(df[selected_col].min(), 2),
                        round(df[selected_col].max(), 2),
                        round(df[selected_col].max() - df[selected_col].min(), 2)
                    ]
                })
                st.dataframe(stats, hide_index=True)
            else:
                stats = pd.DataFrame({
                    'Statistic': ['Unique Values', 'Most Common', 'Least Common', 'Missing Values'],
                    'Value': [
                        df[selected_col].nunique(),
                        f"{df[selected_col].value_counts().index[0]} ({df[selected_col].value_counts().iloc[0]})" if not
                        df[selected_col].value_counts().empty else "N/A",
                        f"{df[selected_col].value_counts().index[-1]} ({df[selected_col].value_counts().iloc[-1]})" if not
                        df[selected_col].value_counts().empty else "N/A",
                        f"{df[selected_col].isnull().sum()} ({round(df[selected_col].isnull().sum() / len(df) * 100, 2)}%)"
                    ]
                })
                st.dataframe(stats, hide_index=True)

        with col2:
            # Visualization based on column type
            if df[selected_col].dtype in ['int64', 'float64']:
                fig, ax = plt.subplots(figsize=(8, 4))
                sns.histplot(df[selected_col].dropna(), kde=True, ax=ax)
                ax.set_title(f'Distribution of {selected_col}')
                st.pyplot(fig)
            else:
                # For categorical, show bar chart of top categories
                value_counts = df[selected_col].value_counts().head(10)
                fig, ax = plt.subplots(figsize=(8, 4))
                value_counts.plot(kind='bar', ax=ax)
                ax.set_title(f'Top 10 values in {selected_col}')
                plt.xticks(rotation=45)
                plt.tight_layout()
                st.pyplot(fig)

        # Show unique values for categorical columns
        if df[selected_col].dtype not in ['int64', 'float64'] and df[selected_col].nunique() < 100:
            st.markdown("<h3 class='section-header'>Unique Values</h3>", unsafe_allow_html=True)
            unique_vals = pd.DataFrame(df[selected_col].value_counts()).reset_index()
            unique_vals.columns = [selected_col, 'Count']
            unique_vals['Percentage'] = round(unique_vals['Count'] / len(df) * 100, 2)
            st.dataframe(unique_vals)

        # Add data filtering
        st.markdown("<h3 class='section-header'>Data Filtering</h3>", unsafe_allow_html=True)
        filter_col = st.selectbox("Select column for filtering", df.columns.tolist(), key="filter_col")

        if df[filter_col].dtype in ['int64', 'float64']:
            min_val, max_val = float(df[filter_col].min()), float(df[filter_col].max())
            filter_range = st.slider(f"Filter range for {filter_col}", min_val, max_val, (min_val, max_val))
            filtered_df = df[(df[filter_col] >= filter_range[0]) & (df[filter_col] <= filter_range[1])]
        else:
            filter_values = st.multiselect(f"Select values for {filter_col}", df[filter_col].unique())
            if filter_values:
                filtered_df = df[df[filter_col].isin(filter_values)]
            else:
                filtered_df = df

        st.markdown(f"Filtered data contains **{len(filtered_df)}** rows")
        st.dataframe(filtered_df.head(10))

        if len(filtered_df) < len(df):
            show_all_filtered = st.checkbox("Show all filtered data")
            if show_all_filtered:
                st.dataframe(filtered_df)

else:
    # Instructions when no data is loaded
    st.info("Please upload a CSV file to start analyzing.")

    # Add example of what the dashboard can do
    st.markdown("""
    ## Features

    - **Data Overview**: Basic information, summary statistics, and data types
    - **Visualizations**: Histograms, scatter plots, bar charts, box plots, and correlation heatmaps
    - **Detailed Analysis**: Column-specific statistics and filtering options

    Upload your CSV file to get started!
    """)