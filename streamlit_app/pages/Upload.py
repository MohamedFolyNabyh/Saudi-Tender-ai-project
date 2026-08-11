import streamlit as st

from api import upload_tender
from auth_guard import require_login


require_login()


st.set_page_config(

    page_title="Upload Tender",

    page_icon="📄",

    layout="wide"

)


st.title("Upload Tender")



# ===========================
# Check Project
# ===========================


if "selected_project" not in st.session_state:

    st.error(

        "Please select a project first."

    )

    st.stop()



project_id = st.session_state.selected_project



# ===========================
# Upload File
# ===========================


uploaded_file = st.file_uploader(

    "Choose Tender File",

    type=["pdf","docx", "txt"]

)



if uploaded_file:


    st.info(

        f"Selected file: {uploaded_file.name}"

    )



st.divider()



col1, col2 = st.columns(2)



# ===========================
# Upload
# ===========================

# ===========================

with col1:

    if st.button(
        "⬆ Upload Tender",
        use_container_width=True,
        disabled=uploaded_file is None
    ):

        try:
            with st.spinner(
                """
                Processing Tender...

                Extracting text
                Creating chunks
                Generating embeddings
                Storing vectors
                """
            ):
                # استدعاء دالة رفع كراسة الشروط والمعالجة
                response = upload_tender(
                    project_id,
                    uploaded_file
                )

                # إظهار رسالة النجاح بعد انتهاء المعالجة
                st.success(f"Tender {response['tender_name']} uploaded successfully")

        except Exception as e:
            # عرض الخطأ للمستخدم في واجهة Streamlit بشكل ناعم
            st.error(f"Failed to upload tender: {str(e)}")