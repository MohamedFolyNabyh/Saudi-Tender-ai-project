import streamlit as st

from api import login


# =========================
# Page Config
# =========================

st.set_page_config(
    page_title="Login",
    page_icon="🔐",
    layout="centered"
)


# =========================
# Initialize Session State
# =========================

if "logged_in" not in st.session_state:

    st.session_state["logged_in"] = False


if "token" not in st.session_state:

    st.session_state["token"] = None


# =========================
# Already Logged In
# =========================

if st.session_state.get("logged_in"):

    st.success("You are already logged in.")

    if st.button(
        "Go to Dashboard",
        use_container_width=True
    ):

        st.switch_page(
            "pages/Dashboard.py"
        )

    st.stop()


# =========================
# Page
# =========================

st.title("🔐 Tender AI")

st.subheader("Login")


# =========================
# Login Form
# =========================

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


# =========================
# Login
# =========================

if submitted:

    # -------------------------
    # Validate Input
    # -------------------------

    if not email or not password:

        st.error(
            "Please enter email and password."
        )

        st.stop()


    # -------------------------
    # Send Login Request
    # -------------------------

    with st.spinner("Logging in..."):

        try:

            token, response = login(
                email=email,
                password=password
            )

        except Exception as e:

            st.error(
                f"Login failed: {e}"
            )

            st.stop()


    # -------------------------
    # Successful Login
    # -------------------------

    if token:

        # Save token in Streamlit session
        st.session_state["token"] = token

        # Mark user as logged in
        st.session_state["logged_in"] = True

        st.success(
            "Login successful."
        )

        # Go to Dashboard
        st.switch_page(
            "pages/Dashboard.py"
        )


    # -------------------------
    # Failed Login
    # -------------------------

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