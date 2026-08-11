import streamlit as st

from auth import login


st.set_page_config(
    page_title="Login",
    page_icon="🔐",
    layout="centered"
)


st.title("🔐 Tender AI")
st.subheader("Login")


if "logged_in" not in st.session_state:

    st.session_state["logged_in"] = False


if st.session_state["logged_in"]:

    st.success("You are already logged in.")

    if st.button("Go to Chat"):

        st.switch_page(
            "pages/Chat.py"
        )

    st.stop()


with st.form("login_form"):

    email = st.text_input(
        "Email",
        placeholder="Enter your email"
    )

    password = st.text_input(
        "Password",
        type="password",
        placeholder="Enter your password"
    )

    submitted = st.form_submit_button(
        "Login",
        use_container_width=True
    )


if submitted:

    if not email or not password:

        st.error(
            "Please enter email and password."
        )

    else:

        with st.spinner("Logging in..."):

            token, response = login(
                email=email,
                password=password
            )

        if token:

            st.success(
                "Login successful."
            )

            st.switch_page(
                "pages/Chat.py"
            )

        else:

            try:
                error = response.json()

                detail = error.get(
                    "detail",
                    "Invalid email or password."
                )

            except Exception:

                detail = (
                    "Invalid email or password."
                )

            st.error(detail)