import streamlit as st

from api import (
    generate_report,
    export_report
)

from auth_guard import require_login


# ==========================
# Authentication
# ==========================

require_login()


# ==========================
# Page Configuration
# ==========================

st.set_page_config(
    page_title="Reports",
    page_icon="📑",
    layout="wide"
)


st.title("📑 Tender Reports")


# ==========================
# Check Selected Tender
# ==========================

tender_id = st.session_state.get(
    "tender_id"
)


if not tender_id:

    st.warning(
        "Please select a tender first from Dashboard."
    )

    if st.button(
        "📂 Go to Dashboard",
        use_container_width=True
    ):

        st.switch_page(
            "pages/Dashboard.py"
        )

    st.stop()


# ==========================
# Selected Tender Information
# ==========================

tender_title = st.session_state.get(
    "tender_title",
    "Selected Tender"
)


project_name = st.session_state.get(
    "project_name",
    "Selected Project"
)


st.info(
    f"Project: **{project_name}**"
)

st.info(
    f"Tender: **{tender_title}**"
)


# ==========================
# Reports Memory
# ==========================

if "reports" not in st.session_state:

    st.session_state["reports"] = {}


if tender_id not in st.session_state["reports"]:

    st.session_state["reports"][tender_id] = {}


reports = st.session_state["reports"][tender_id]


# ==========================
# Report Type
# ==========================

report_type = st.selectbox(
    "Select Report",
    [
        "Summary",
        "Risk"
    ]
)


# ==========================
# Generate Report
# ==========================

if st.button(
    "📑 Generate Report",
    use_container_width=True
):

    # --------------------------
    # Existing Report
    # --------------------------

    if report_type in reports:

        st.info(
            "Report already exists. Regenerating..."
        )


    # --------------------------
    # Generate
    # --------------------------

    with st.spinner(
        f"Generating {report_type} report..."
    ):

        try:

            response = generate_report(
                tender_id=tender_id,
                report_type=report_type
            )


            # ======================
            # Get Report Content
            # ======================

            if isinstance(
                response,
                dict
            ):

                content = (
                    response.get("answer")
                    or response.get("content")
                    or response.get("report")
                )

                if not content:

                    content = str(
                        response
                    )

            else:

                content = str(
                    response
                )


            # ======================
            # Filename
            # ======================

            filename = (
                f"tender_{tender_id}_"
                f"{report_type.lower()}.pdf"
            )


            # ======================
            # Save Report
            # ======================

            reports[report_type] = {

                "content": content,

                "sources": (
                    response.get(
                        "sources",
                        []
                    )
                    if isinstance(
                        response,
                        dict
                    )
                    else []
                ),

                "filename": filename
            }


            # ======================
            # Remove Old PDF
            # ======================

            pdf_key = (
                f"pdf_{tender_id}_"
                f"{report_type}"
            )


            if pdf_key in st.session_state:

                del st.session_state[pdf_key]


            st.success(
                "Report Generated Successfully."
            )


        except Exception as e:

            st.error(
                f"Failed to generate report: {e}"
            )


# ==========================
# Display Report
# ==========================

if report_type in reports:

    report = reports[report_type]


    st.divider()


    # ==========================
    # Report Header
    # ==========================

    st.subheader(
        f"📊 {report_type} Report"
    )


    # ==========================
    # Report Content
    # ==========================

    st.markdown(
        report["content"]
    )


    # ==========================
    # Sources
    # ==========================

    if report.get("sources"):

        st.divider()

        with st.expander(
            "📚 Sources"
        ):

            for source in report["sources"]:

                if isinstance(
                    source,
                    dict
                ):

                    page = source.get(
                        "page",
                        "Unknown"
                    )

                    source_name = source.get(
                        "source",
                        "Unknown"
                    )

                    st.write(
                        f"Page: {page} | "
                        f"Source: {source_name}"
                    )

                else:

                    st.write(
                        source
                    )


    st.divider()


    # ==========================
    # Actions
    # ==========================

    col1, col2 = st.columns(2)


    # ==========================
    # Prepare PDF
    # ==========================

    with col1:

        if st.button(
            "📄 Prepare PDF",
            use_container_width=True
        ):

            with st.spinner(
                "Creating PDF..."
            ):

                try:

                    pdf_bytes = export_report(
                        report["content"],
                        report["filename"]
                    )


                    st.session_state[
                        f"pdf_{tender_id}_{report_type}"
                    ] = pdf_bytes


                    st.success(
                        "PDF is ready."
                    )


                except Exception as e:

                    st.error(
                        f"Failed to create PDF: {e}"
                    )


    # ==========================
    # Clear Report
    # ==========================

    with col2:

        if st.button(
            "🗑️ Clear Report",
            use_container_width=True
        ):

            # Remove report

            del reports[
                report_type
            ]


            # Remove generated PDF

            pdf_key = (
                f"pdf_{tender_id}_"
                f"{report_type}"
            )


            if pdf_key in st.session_state:

                del st.session_state[
                    pdf_key
                ]


            st.rerun()


    # ==========================
    # Download PDF
    # ==========================

    pdf_key = (
        f"pdf_{tender_id}_"
        f"{report_type}"
    )


    if pdf_key in st.session_state:

        st.divider()


        st.download_button(

            label="⬇️ Download PDF",

            data=st.session_state[
                pdf_key
            ],

            file_name=report["filename"],

            mime="application/pdf",

            use_container_width=True
        )


# ==========================
# Navigation
# ==========================

st.divider()


if st.button(
    "📂 Back to Dashboard",
    use_container_width=True
):

    st.switch_page(
        "pages/Dashboard.py"
    )