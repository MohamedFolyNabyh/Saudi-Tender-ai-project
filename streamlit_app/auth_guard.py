import streamlit as st

from auth import is_logged_in



def require_login():

    if not is_logged_in():

        st.warning(
            "Please login first."
        )

        st.switch_page(
            "pages/Login.py"
        )

        st.stop()