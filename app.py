import streamlit as st
import pandas as pd
import zipfile
import io

st.set_page_config(page_title="CSV Splitter (500 Rows)", layout="wide")

st.title("📊 CSV Splitter & Row Cleaner")
st.write("Upload a CSV, remove selected rows, and split into 500-row chunks.")

# Upload CSV
uploaded_file = st.file_uploader("Upload CSV File", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.success(f"Loaded {len(df)} rows")

    # Show data
    st.subheader("📄 CSV Preview")
    st.dataframe(df, use_container_width=True)

    # Row removal
    st.subheader("🗑️ Select Rows to Remove")
    rows_to_remove = st.multiselect(
        "Select row indexes to remove",
        options=df.index.tolist()
    )

    if st.button("🚀 Clean & Split CSV"):
        # Remove rows
        cleaned_df = df.drop(index=rows_to_remove)

        st.success(f"Remaining rows: {len(cleaned_df)}")

        # Split into 500-row chunks
        chunk_size = 500
        chunks = [
            cleaned_df.iloc[i:i + chunk_size]
            for i in range(0, len(cleaned_df), chunk_size)
        ]

        # Create ZIP of chunks
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zip_file:
            for i, chunk in enumerate(chunks):
                csv_buffer = io.StringIO()
                chunk.to_csv(csv_buffer, index=False)
                zip_file.writestr(f"csv_chunk_{i + 1}.csv", csv_buffer.getvalue())

        zip_buffer.seek(0)

        # Downloads
        st.subheader("⬇️ Downloads")

        st.download_button(
            label="Download Cleaned CSV",
            data=cleaned_df.to_csv(index=False),
            file_name="cleaned_csv.csv",
            mime="text/csv"
        )

        st.download_button(
            label="Download 500-Row CSV Chunks (ZIP)",
            data=zip_buffer,
            file_name="csv_chunks_500_rows.zip",
            mime="application/zip"
        )
