import streamlit as st

from auth_guard import require_login
from auth import logout
from api import (
    chat,
    get_projects,
    get_tenders
)


# =====================================
# Page Configuration
# =====================================

st.set_page_config(
    page_title="Tender AI Chat",
    page_icon="🤖",
    layout="wide"
)


# =====================================
# Authentication
# =====================================

require_login()


# =====================================
# Header
# =====================================

header_col1, header_col2 = st.columns(
    [5, 1]
)

with header_col1:

    st.title("🤖 Tender AI Chat")

with header_col2:

    if st.button(
        "Logout",
        use_container_width=True
    ):

        logout()


# =====================================
# Initialize Chat History
# =====================================

if "chat_history" not in st.session_state:

    st.session_state.chat_history = {}


# =====================================
# Load Projects
# =====================================

try:

    projects = get_projects()

except Exception as e:

    st.error(
        f"Failed to load projects: {e}"
    )

    st.stop()


if not projects:

    st.info(
        "No projects found."
    )

    st.stop()


# =====================================
# Project Selection
# =====================================

project_options = {
    project["name"]: project["id"]
    for project in projects
}


selected_project_name = st.selectbox(
    "Select Project",
    list(project_options.keys())
)


selected_project_id = project_options[
    selected_project_name
]


# =====================================
# Load Tenders
# =====================================

try:

    tenders = get_tenders(
        selected_project_id
    )

except Exception as e:

    st.error(
        f"Failed to load tenders: {e}"
    )

    st.stop()


if not tenders:

    st.info(
        "No tenders found for this project."
    )

    st.stop()


# =====================================
# Tender Selection
# =====================================

tender_options = {
    tender["tender_name"]: tender["id"]
    for tender in tenders
}


selected_tender_name = st.selectbox(
    "Select Tender",
    list(tender_options.keys())
)


tender_id = tender_options[
    selected_tender_name
]


# =====================================
# Chat Session
# =====================================

if tender_id not in st.session_state.chat_history:

    st.session_state.chat_history[tender_id] = []


history = st.session_state.chat_history[
    tender_id
]


# =====================================
# Display Previous Messages
# =====================================

for message in history:

    with st.chat_message(
        message["role"]
    ):

        st.markdown(
            message["content"]
        )


# =====================================
# User Question
# =====================================

question = st.chat_input(
    "Ask anything about this tender..."
)


if question:

    # -----------------------------
    # Display User Message
    # -----------------------------

    history.append({

        "role": "user",

        "content": question

    })


    with st.chat_message("user"):

        st.markdown(question)


    # -----------------------------
    # Generate Answer
    # -----------------------------

    with st.chat_message("assistant"):

        with st.spinner(
            "Analyzing tender..."
        ):

            try:

                result = chat(

                    tender_id=tender_id,

                    question=question

                )

                answer = result.get(
                    "answer",
                    "No answer returned."
                )

                sources = result.get(
                    "sources",
                    []
                )

            except Exception as e:

                answer = (
                    f"Error while processing "
                    f"your question: {e}"
                )

                sources = []


        st.markdown(answer)


        # -----------------------------
        # Sources
        # -----------------------------

        if sources:

            with st.expander(
                "📚 Sources"
            ):

                for source in sources:

                    st.markdown(
                        f"- {source}"
                    )


    # -----------------------------
    # Save Assistant Message
    # -----------------------------

    history.append({

        "role": "assistant",

        "content": answer

    })