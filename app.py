import streamlit as st # type: ignore
import pandas as pd # type: ignore
import os
from io import BytesIO

# ---- PAGE CONFIGURATION ----
st.set_page_config(page_title="Data Sweeper", layout="wide")

# ---- CUSTOM CSS ----
st.markdown("""
    <style>
        /* Full Page Background */
        body { background-color: #f4f7f9; }

        /* Centered Content */
        .center-text {
            text-align: center;
            color: #2C3E50;
        }

        /* HEADER Styling */
        .header-container {
            text-align: center;
            padding: 25px;
            background: linear-gradient(135deg, #5B86E5, #36D1DC); 
            border-radius: 12px;
            color: white;
            box-shadow: 0px 5px 15px rgba(0, 0, 0, 0.2);
        }
        .header-title {
            font-size: 38px;
            font-weight: bold;
            letter-spacing: 1px;
            margin-bottom: 8px;
        }
        .header-subtitle {
            font-size: 18px;
            font-weight: 400;
            opacity: 0.9;
        }

        /* File Upload Section */
        .upload-section { 
            padding: 20px; 
            border: 2px dashed #3498DB; 
            border-radius: 12px; 
            background-color: #ecf5ff;
            text-align: center;
        }

        /* Data Table Styling */
        .stDataFrame {
            border-radius: 10px;
            border: 1px solid #ddd;
            box-shadow: 2px 2px 8px rgba(0, 0, 0, 0.1);
        }

        /* Buttons */
        .stButton > button {
            width: 100%;
            border-radius: 8px;
            font-weight: bold;
            background-color: #2980b9;
            color: white;
            padding: 10px;
            transition: 0.3s;
        }
        .stButton > button:hover {
            background-color: #1a5276;
        }

        /* Download Button */
        .stDownloadButton > button {
            width: 100%;
            border-radius: 8px;
            background-color: #27AE60;
            color: white;
            font-weight: bold;
            padding: 10px;
            transition: 0.3s;
        }
        .stDownloadButton > button:hover {
            background-color: #1e8449;
        }

        /* Success Message */
        .success-message {
            text-align: center; 
            padding: 15px; 
            background: linear-gradient(135deg, #42E695, #3BB2B8); 
            color: white;
            border-radius: 12px;
            box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.15);
            margin-top: 20px;
        }
    </style>
""", unsafe_allow_html=True)

# ---- HEADER ----
st.markdown("""
    <div class="header-container">
        <h1 class="header-title">🚀 HG Streamlit</h1>
        <p class="header-subtitle">Effortlessly transform, clean, and visualize your data.</p>
    </div>
""", unsafe_allow_html=True)

# ---- FILE UPLOAD SECTION ----
st.markdown("""
    <div class="upload-section">
        <h2 style="color: #2E86C1; font-size: 28px;">📂 Upload Your Data Files</h2>
        <p style="font-size: 16px; color: #555;">
            Supports <b>CSV, Excel (XLSX), and ODS</b> file formats.
        </p>
    </div>
""", unsafe_allow_html=True)

uploaded_files = st.file_uploader(
    label="Choose files to upload",
    type=["csv", "xlsx", "ods"],
    accept_multiple_files=True
)

if uploaded_files:
    for file in uploaded_files:
        file_ext = os.path.splitext(file.name)[-1].lower()
        
        try:
            # ---- LOAD FILE BASED ON TYPE ----
            if file_ext == ".csv":
                df = pd.read_csv(file)
            elif file_ext == ".xlsx":
                df = pd.read_excel(file, engine="openpyxl")
            elif file_ext == ".ods":
                df = pd.read_excel(file, engine="odf")
            else:
                st.error(f"❌ Unsupported file type: {file_ext}")
                continue

            # ---- FILE DETAILS ----
            st.markdown(f"<h3 class='center-text'>📄 {file.name}</h3>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align: center; font-size: 16px;'><strong>Size:</strong> {file.size / 1024:.2f} KB</p>", unsafe_allow_html=True)

            # ---- DATA PREVIEW ----
            st.markdown("#### 🔍 Data Preview")
            st.dataframe(df.head())

            # ---- DATA CLEANING ----
            st.markdown("### 🧹 Data Cleaning Options")
            if st.checkbox(f"Enable Cleaning for `{file.name}`"):
                col1, col2 = st.columns(2)

                with col1:
                    if st.button(f"🗑 Remove Duplicates from {file.name}"):
                        df.drop_duplicates(inplace=True)
                        st.success("✔ Duplicates Removed Successfully!")

                with col2:
                    if st.button(f"🛠 Fill Missing Values for {file.name}"):
                        numeric_cols = df.select_dtypes(include=['number']).columns
                        df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
                        st.success("✔ Missing Values Filled!")

            # ---- COLUMN SELECTION ----
            st.markdown("### 🎯 Choose Columns to Keep")
            selected_columns = st.multiselect(f"📌 Select columns for `{file.name}`", df.columns, default=df.columns)
            df = df[selected_columns]

            # ---- DATA VISUALIZATION ----
            st.markdown("### 📊 Data Visualization")
            if st.checkbox(f"📈 Show Visualization for `{file.name}`"):
                st.bar_chart(df.select_dtypes(include='number').iloc[:, :2])

            # ---- FILE CONVERSION ----
            st.markdown("### 🔄 Convert File Format")
            conversion_type = st.radio(f"📝 Convert `{file.name}` to:", ["CSV", "Excel"], key=file.name + "_convert")

            if st.button(f"📥 Convert `{file.name}`"):
                buffer = BytesIO()

                if conversion_type == "CSV":
                    df.to_csv(buffer, index=False)
                    file_name = file.name.replace(file_ext, ".csv")
                    mime_type = "text/csv"
                elif conversion_type == "Excel":
                    df.to_excel(buffer, index=False, engine="xlsxwriter")
                    file_name = file.name.replace(file_ext, ".xlsx")
                    mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

                buffer.seek(0)

                st.download_button(
                    label="📩 Download Converted File",
                    data=buffer,
                    file_name=file_name,
                    mime=mime_type
                )

        except Exception as e:
            st.error(f"⚠️ Error processing `{file.name}`: {e}")

# Success message
st.markdown("""
    <div class="success-message">
        <h3>✅ All files processed successfully!</h3>
    </div>
""", unsafe_allow_html=True)
