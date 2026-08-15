import streamlit as st

from api import (
    get_tenders,
    compare_tenders
)

from auth_guard import require_login


# ===========================
# Authentication
# ===========================

require_login()


# ===========================
# Page Config
# ===========================

st.set_page_config(
    page_title="Compare Tenders",
    page_icon="⚖️",
    layout="wide"
)


# ===========================
# Page
# ===========================

st.title("⚖️ Tender Comparison")


# ===========================
# Check Project
# ===========================

# استخدام المفتاح الموحد selected_project مع دعم project_id كـ fallback
project_id = st.session_state.get("selected_project") or st.session_state.get("project_id")


if not project_id:

    st.warning(
        "Please select a project first from Dashboard."
    )

    if st.button(
        "📂 Go to Dashboard",
        use_container_width=True
    ):

        st.switch_page(
            "pages/Dashboard.py"
        )

    st.stop()


# ===========================
# Project Name
# ===========================

project_name = st.session_state.get(
    "selected_project_name",
    st.session_state.get("project_name", "Selected Project")
)


st.info(
    f"Selected Project: **{project_name}** (`{project_id}`)"
)


# ===========================
# Load Tenders
# ===========================

try:

    tenders = get_tenders(
        project_id
    )

except Exception as e:

    st.error(
        f"Failed to load tenders: {e}"
    )

    st.stop()


# ===========================
# Check Tenders
# ===========================

if not tenders:

    st.warning(
        "No tenders available for this project."
    )

    if st.button(
        "📤 Upload Tenders Now",
        use_container_width=True
    ):
        st.switch_page("pages/Upload.py")

    st.stop()


if len(tenders) < 2:

    st.warning(
        "You need at least two tenders in this project to compare."
    )

    if st.button(
        "📤 Upload Another Tender",
        use_container_width=True
    ):
        st.switch_page("pages/Upload.py")

    st.stop()


# ===========================
# Tender Options
# ===========================

tender_options = {

    tender.get("tender_name", f"Tender {tender.get('id')}"): tender["id"]

    for tender in tenders

}


# ===========================
# Tender Selection
# ===========================

st.subheader(
    "Select Tenders"
)


col1, col2 = st.columns(2)

options_list = list(tender_options.keys())

with col1:

    tender_a_name = st.selectbox(

        "First Tender",

        options=options_list,

        index=0,

        key="compare_tender_a"

    )


with col2:

    # تحديد العنصر الثاني تلقائياً لتجنب تكرار الأول
    default_b_idx = 1 if len(options_list) > 1 else 0

    tender_b_name = st.selectbox(

        "Second Tender",

        options=options_list,

        index=default_b_idx,

        key="compare_tender_b"

    )


tender_a = tender_options[
    tender_a_name
]


tender_b = tender_options[
    tender_b_name
]


# ===========================
# Compare Key
# ===========================

compare_key = (
    f"compare_{project_id}_{tender_a}_{tender_b}"
)


# ===========================
# Compare Button
# ===========================

if st.button(

    "⚖️ Compare Tenders",

    use_container_width=True

):

    # -----------------------
    # Same Tender
    # -----------------------

    if tender_a == tender_b:

        st.warning(

            "Please select two different tenders to perform a comparison."

        )

        st.stop()


    # -----------------------
    # Compare Execution
    # -----------------------

    with st.spinner(
        "Analyzing and comparing tenders..."
    ):

        try:

            response = compare_tenders(

                tender_a,

                tender_b

            )

        except Exception as e:

            st.error(
                f"Comparison failed: {e}"
            )

            st.stop()


    # -----------------------
    # Extract Answer Text
    # -----------------------

    if isinstance(response, dict):

        answer = (
            response.get("answer") or
            response.get("content") or
            response.get("result") or
            str(response)
        )

    else:

        answer = str(response)


    # -----------------------
    # Save Result to Session State
    # -----------------------

    st.session_state[compare_key] = answer


# ===========================
# Display Result
# ===========================

if compare_key in st.session_state:

    st.divider()

    st.subheader(
        "📊 Comparison Result"
    )

    st.markdown(
        st.session_state[compare_key]
    )


# ===========================
# Navigation
# ===========================

st.divider()

col_back, col_upload = st.columns(2)

with col_back:
    if st.button(
        "📂 Back to Dashboard",
        use_container_width=True
    ):

        st.switch_page(
            "pages/Dashboard.py"
        )

with col_upload:
    if st.button(
        "📤 Upload More Tenders",
        use_container_width=True
    ):

        st.switch_page(
            "pages/Upload.py"
        )