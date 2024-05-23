import streamlit as st
import pandas as pd

# Using the wide layout
st.set_page_config(layout="wide")

st.sidebar.title('Very Basic Data Reader')

# This function will be cached
@st.cache_data
def load_data(file):
    return pd.read_csv(file)

# Sidebar: File Upload
uploaded_file = st.sidebar.file_uploader("Upload a CSV file", type=['csv'])

# Initialize an empty DataFrame
df = pd.DataFrame()

if uploaded_file is not None:
    df = load_data(uploaded_file)

# Filter functionality
if not df.empty:
    filter_columns = st.sidebar.multiselect('Select columns to filter on', df.columns)

    # Creating a dictionary to store the filter values for each filter column
    filters = {}
    for col in filter_columns:
        # Check if the column is numeric
        if pd.api.types.is_numeric_dtype(df[col]):
            df[col] = pd.to_numeric(df[col], errors='coerce')
            min_value = int(df[col].min())
            max_value = int(df[col].max())
            values = st.sidebar.slider(f'Select range for {col}', min_value, max_value, (min_value, max_value), key=col)
            filters[col] = ('numeric', values)
        else:
            # For non-numeric columns, check if there are less than 20 unique values
            unique_values = df[col].dropna().unique()
            if len(unique_values) < 50:
                options = st.sidebar.multiselect(f'Select values for {col}', unique_values, default=unique_values, key=col)
                filters[col] = ('categorical', options)

    # Applying the filters to the DataFrame
    for col, (filter_type, values) in filters.items():
        if filter_type == 'numeric':
            min_val, max_val = values
            df = df[(df[col] >= min_val) & (df[col] <= max_val)]
        elif filter_type == 'categorical':
            df = df[df[col].isin(values)]

# Display functionality
n_cols = st.number_input('Number of columns', min_value=1, max_value=3, step=1)

if len(df) > 0:
    current_index = st.number_input('Enter the index of the row to display', min_value=0, max_value=df.shape[0]-1, value=0, step=1)

st_cols = st.columns(n_cols)

if not df.empty:
    for i, st_col in enumerate(st_cols):
        cols = st_col.multiselect('Select columns to display', df.columns, key=f"col{i}")

        # Display selected row
        if current_index < df.shape[0]:
            row = df.iloc[current_index]
            for col in cols:
                st_col.markdown(f"### {col}")
                st_col.write(row[col])
else:
    for i, st_col in enumerate(st_cols):
        cols = st_col.multiselect('Select columns to display', df.columns, key=f"col{i}")r
    st.write("No CSV uploaded yet or filters result in empty data.")
