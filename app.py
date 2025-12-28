import streamlit as st
import pandas as pd
import zipfile
import io
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

st.set_page_config(
    page_title="Fast CSV Cleaner & Splitter",
    layout="wide"
)

st.title("⚡ Fast CSV Cleaner & 500-Row Splitter")
st.caption("Select rows instantly, remove them, and split CSVs at scale.")

# Upload
uploaded_file = st.file_uploader("📤 Upload CSV", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.success(f"Loaded {len(df):,} rows")

    # Controls
    st.subheader("⚙️ Controls")
    col1, col2 = st.columns(2)

    with col1:
        chunk_size = st.slider(
            "Chunk size",
            min_value=100,
            max_value=2000,
            step=100,
            value=500
        )

    with col2:
        st.write(" ")
        st.write(" ")
        run = st.button("🚀 Remove Selected & Split CSV")

    # AgGrid setup
    st.subheader("📊 Select Rows to REMOVE")

    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_default_column(
        filter=True,
        sortable=True,
        resizable=True
    )
    gb.configure_selection(
        selection_mode="multiple",
        use_checkbox=True
    )
    gb.configure_pagination(
        paginationAutoPageSize=False,
        paginationPageSize=25
    )

    grid_options = gb.build()

    grid_response = AgGrid(
        df,
        gridOptions=grid_options,
        update_mode=GridUpdateMode.SELECTION_CHANGED,
        height=500,
        theme="balham"
    )

    selected_rows = grid_response["selected_rows"]

    st.info(f"Selected rows to remove: {len(selected_rows)}")

    if run:
        if selected_rows:
            selected_df = pd.DataFrame(selected_rows)
            cleaned_df = df.drop(index=selected_df.index)
        else:
            cleaned_df = df.copy()

        st.success(f"Remaining rows: {len(cleaned_df):,}")

        # Split into chunks
        chunks = [
            cleaned_df.iloc[i:i + chunk_size]
            for i in range(0, len(cleaned_df), chunk_size)
        ]

        # ZIP creation
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zip_file:
            for i, chunk in enumerate(chunks, start=1):
                csv_buffer = io.StringIO()
                chunk.to_csv(csv_buffer, index=False)
                zip_file.writestr(
                    f"csv_chunk_{i}_rows_{len(chunk)}.csv",
                    csv_buffer.getvalue()
                )

        zip_buffer.seek(0)

        # Downloads
        st.subheader("⬇️ Download Files")

        col1, col2 = st.columns(2)

        with col1:
            st.download_button(
                "Download Cleaned CSV",
                data=cleaned_df.to_csv(index=False),
                file_name="cleaned_csv.csv",
                mime="text/csv"
            )

        with col2:
            st.download_button(
                "Download CSV Chunks (ZIP)",
                data=zip_buffer,
                file_name="csv_chunks.zip",
                mime="application/zip"
            )
