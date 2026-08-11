import streamlit as st

from api import (
    get_projects,
    get_tenders,
    check_response
)

st.set_page_config(
    page_title="Dashboard",
    page_icon="📂"
)

if "token" not in st.session_state:
    st.switch_page("pages/Login.py")

st.title("Projects")

try:

    projects = check_response(
        get_projects(
            st.session_state.token
        )
    )

except Exception as e:

    st.error(str(e))
    st.stop()

if not projects:

    st.warning("No Projects Found")
    st.stop()

project_names = {
    project["name"]: project["id"]
    for project in projects
}

selected_project = st.selectbox(
    "Select Project",
    list(project_names.keys())
)

project_id = project_names[selected_project]

try:

    tenders = check_response(

        get_tenders(
            project_id,
            st.session_state.token
        )

    )

except Exception as e:

    st.error(str(e))
    st.stop()

if not tenders:

    st.info("No Tenders Found")
    st.stop()

tender_names = {
    tender["title"]: tender["id"]
    for tender in tenders
}

selected_tender = st.selectbox(
    "Select Tender",
    list(tender_names.keys())
)

if st.button(
    "Open Tender",
    use_container_width=True
):

    st.session_state.project_id = project_id

    st.session_state.tender_id = tender_names[
        selected_tender
    ]

    st.session_state.tender_title = selected_tender

    st.switch_page(
        "pages/Chat.py"
    )