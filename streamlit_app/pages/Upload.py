import streamlit as st

from api import (
    upload_tender,
    get_projects,
    get_tenders
)

from auth_guard import require_login


# ===========================
# Authentication
# ===========================

require_login()


# ===========================
# Page Configuration
# ===========================

st.set_page_config(
    page_title="Upload Tender",
    page_icon="📄",
    layout="wide"
)


st.title("📄 Upload Tender")


# ===========================
# Check Project
# ===========================

if "selected_project" not in st.session_state:

    st.warning(
        "Please select a project first."
    )

    st.info(
        "Go to Dashboard and select a project."
    )

    if st.button(
        "📂 Go to Dashboard",
        use_container_width=True
    ):

        st.switch_page(
            "pages/Dashboard.py"
        )

    st.stop()


project_id = st.session_state["selected_project"]


# ===========================
# Project Information
# ===========================

st.success(
    f"Selected Project ID: {project_id}"
)


# ===========================
# Upload File
# ===========================

st.subheader("Choose Tender File")


uploaded_file = st.file_uploader(

    "Upload PDF, DOCX or TXT",

    type=[
        "pdf",
        "docx",
        "txt"
    ]
)


if uploaded_file:

    st.info(
        f"📄 Selected file: **{uploaded_file.name}**"
    )


st.divider()


# ===========================
# Upload Button
# ===========================

if st.button(
    "⬆️ Upload Tender",
    use_container_width=True,
    disabled=uploaded_file is None
):

    try:

        with st.spinner(
            """
            Processing Tender...

            Extracting text...

            Creating chunks...

            Generating embeddings...

            Storing vectors...

            Please wait.
            """
        ):

            response = upload_tender(
                project_id,
                uploaded_file
            )


        # ===========================
        # Success
        # ===========================

        tender_name = response.get(
            "tender_name",
            uploaded_file.name
        )

        tender_id = response.get(
            "id"
        )


        st.success(
            f"✅ Tender **{tender_name}** uploaded successfully."
        )


        if tender_id:

            st.info(
                f"Tender ID: {tender_id}"
            )


        # ===========================
        # Refresh Tenders
        # ===========================

        try:

            tenders = get_tenders(
                project_id
            )

            st.session_state["tenders"] = tenders

        except Exception:

            pass


        # ===========================
        # Go To Dashboard
        # ===========================

        if st.button(
            "📂 Back to Dashboard",
            use_container_width=True
        ):

            st.switch_page(
                "pages/Dashboard.py"
            )


    except Exception as e:

        st.error(
            f"❌ Failed to upload tender: {str(e)}"
        )


