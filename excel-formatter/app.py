import streamlit as st
import pandas as pd
import re
from datetime import datetime
import io
import random
import difflib
from utils import ai_column_formatter,process_dataframe

def preprocess_file(df):
    df.dropna(how='all', inplace=True)
    df.dropna(axis=1, how='all', inplace=True)
    return df

st.set_page_config(page_title="AI Consolidator | MAS Intimates", layout="wide")

# Custom CSS for better styling
st.markdown("""
<style>
    .main {
        padding: 2rem;
    }
    .stButton button {
        background-color: #4CAF50;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        border: none;
        font-weight: bold;
    }
    .stButton button:hover {
        background-color: #45a049;
    }
    .download-btn {
        background-color: #008CBA;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        text-decoration: none;
        font-weight: bold;
    }
    .header-section {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 5px;
        margin-bottom: 1rem;
    }
    .result-section {
        background-color: #f1f8e9;
        padding: 1rem;
        border-radius: 5px;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Title and description
st.title("AI Consolidator | MAS Intimates")
st.markdown("Upload your Excel or CSV file and let AI standardize your column names.")

# File upload section
st.markdown('<div class="header-section">', unsafe_allow_html=True)
st.header("1. Upload Your File")

uploaded_file = st.file_uploader("Choose an Excel or CSV file", type=['xlsx', 'xls', 'csv'])
st.markdown('</div>', unsafe_allow_html=True)


if uploaded_file is not None:
    try:
        # Read the file
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        df = preprocess_file(df)
        st.success(f"File uploaded successfully! Found {len(df.columns)} columns and {len(df)} rows.")
        
        # Show a sample of the uploaded data
        st.subheader("Sample of Uploaded Data")
        st.dataframe(df.head(5))
    
        # Process button
        st.markdown('<div class="header-section">', unsafe_allow_html=True)
        st.header("2. Process with AI")
        col1, col2, col3 = st.columns([3, 3, 1])  # Adjust widths to control size
        # Column 1: Input for Header Row
        with col1:
            col11, col12 = st.columns([1, 1])
            with col11:
                header_row = st.text_input(label="Header Row",placeholder="e.g., 0,2")
            with col12:
                num_rows = st.text_input(label="No. of Rows",placeholder="e.g., 10")
        # Column 2: Input for No. of Rows
        with col2:
            pass
        # Column 3: Submit Button
        with col3:
            pass
        process_button = st.button("🧠 Process with AI")
        st.markdown('</div>', unsafe_allow_html=True)
        
        if process_button:
            # Simulate AI processing with a progress bar
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i in range(101):
                # Update progress bar
                progress_bar.progress(i)
                
                # Update status text based on progress
                if i < 30:
                    status_text.text(f"Analyzing column names... {i}%")
                elif i < 60:
                    status_text.text(f"Detecting patterns... {i}%")
                elif i < 90:
                    status_text.text(f"Applying AI mapping... {i}%")
                else:
                    status_text.text(f"Finalizing results... {i}%")
                
                # Add a small delay to simulate processing
                if i % 10 == 0:
                    import time
                    time.sleep(0.1)
            
            header_row_val = header_row if header_row else None
            num_rows_val = num_rows if num_rows else None
            # Get column mapping
            mapping,parsed_json,fdf = ai_column_formatter(df,header_row_val,num_rows_val)
            
            # Display mapping results
            st.markdown('<div class="result-section">', unsafe_allow_html=True)
            st.header("3. AI Processing Results")
            
            # Column Mapping Results
            st.dataframe(mapping)
            
            # Process the DataFrame based on the mapping
            processed_df = process_dataframe(parsed_json,fdf)
            
            # Display processed DataFrame
            st.header("4. Processed Output")
            
            # Count date columns
            # date_columns = [col for col in processed_df.columns if col.startswith('Date:')]
            
            # st.markdown(f"""
            # **Summary:**
            # - Records: {len(processed_df)}
            # - Date columns detected: {len(date_columns)}
            # """)
            
            st.dataframe(processed_df.head(10))
            
            # Download button for processed data
            st.header("5. Download Processed Data")
            
            csv = processed_df.to_csv(index=False)
            st.download_button(
                label="📥 Download Processed CSV",
                data=csv,
                file_name="processed_data.csv",
                mime="text/csv"
            )
            st.markdown('</div>', unsafe_allow_html=True)
            
    except Exception as e:
        st.error(f"Error processing file: {str(e)}")
else:
    # Sample data for demonstration
    st.markdown("""
    ### 📊 Example
    
    This app will help you standardize column names in your spreadsheets. For example, it can:
    
    - Identify columns like "Style_ID", "ID", or "SID" as "Style ID"
    - Recognize "Style Description", "DESCR" as "Style"
    - Detect date columns with various formats (2024-09-01, Sept 2024, etc.)
    
    Upload a file to get started!
    """)

# Add footer
st.markdown("---")
st.markdown("Built with Streamlit and AI 🚀")