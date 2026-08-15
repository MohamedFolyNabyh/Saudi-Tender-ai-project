import streamlit as st
from api import register

st.set_page_config(
    page_title="Register",
    page_icon="📝"
)

st.title("Tender AI")

st.subheader("Create Account")

with st.form("register"):
    full_name = st.text_input("Full Name")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    
    submit = st.form_submit_button("Register")

if submit:
    # 1. التحقق البسيط من إدخال البيانات
    if not email or not password or not full_name:
        st.warning("Please fill in all fields.")
    else:
        try:
            # 2. استدعاء الدالة داخل try لمسك أي Exception صادرة من api.py
            response = register(
                email=email,
                password=password,
                full_name=full_name
            )
            
            st.success("Account Created Successfully!")
            st.switch_page("pages/Login.py")

        except Exception as e:
            # 3. عرض نص الخطأ من السيرفر بدون توقف التطبيق
            err_msg = str(e)

            # إذا كانت الرسالة تحتوي على تفاصيل Validation من Pydantic
            if "string_too_short" in err_msg or "at least 6 characters" in err_msg:
                st.error("Password must be at least 6 characters long.")
            elif "already exists" in err_msg.lower():
                st.error("An account with this email already exists.")
            else:
                st.error(err_msg)
            

st.divider()

if st.button("Already have an account? Login"):
    st.switch_page("pages/Login.py")