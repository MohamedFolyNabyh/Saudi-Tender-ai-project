import streamlit as st

from api import compare_tenders
from auth_guard import require_login


require_login()


st.set_page_config(

    page_title="Compare Tenders",

    page_icon="⚖️",

    layout="wide"

)


st.title("Tender Comparison")



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
# Load Tenders
# ===========================

if "tenders" not in st.session_state:

    st.error(
        "No tenders available."
    )

    st.stop()



tenders = st.session_state.tenders



if len(tenders) < 2:

    st.warning(

        "You need at least two tenders to compare."

    )

    st.stop()



# ===========================
# Tender Options
# ===========================


tender_options = {

    tender["file_name"]: tender["id"]

    for tender in tenders

}



# ===========================
# Selection
# ===========================


col1, col2 = st.columns(2)



with col1:

    tender_a_name = st.selectbox(

        "First Tender",

        options=list(tender_options.keys()),

        key="compare_tender_a"

    )



with col2:

    tender_b_name = st.selectbox(

        "Second Tender",

        options=list(tender_options.keys()),

        key="compare_tender_b"

    )



tender_a = tender_options[tender_a_name]

tender_b = tender_options[tender_b_name]



compare_key = f"compare_{project_id}"



# ===========================
# Compare
# ===========================


if st.button(

    "Compare",

    use_container_width=True

):


    if tender_a == tender_b:

        st.warning(

            "Please select two different tenders."

        )

        st.stop()



    with st.spinner(

        "Analyzing tenders..."

    ):


        response = compare_tenders(

            tender_a,

            tender_b

        )


    st.session_state[compare_key] = response["answer"]



# ===========================
# Display Result
# ===========================


if compare_key in st.session_state:


    st.divider()


    st.subheader(

        "Comparison Result"

    )


    st.markdown(

        st.session_state[compare_key]

    )