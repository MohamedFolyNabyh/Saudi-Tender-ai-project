import streamlit as st

from api import (
    get_projects,
    create_project,
    get_tenders
)

from auth_guard import require_login


# ===========================
# Authentication
# ===========================

require_login()


# ===========================
# Page Configuration
# ===========================

st.set_page_config(
    page_title="Dashboard",
    page_icon="📂",
    layout="wide"
)

st.title("📂 Dashboard")


# ===========================
# Fetch Projects
# ===========================

try:
    projects = get_projects()
except Exception as e:
    st.error(f"❌ Failed to load projects: {str(e)}")
    st.stop()


# ===========================
# Project Selection / Switch
# ===========================

st.subheader("Select Active Project")

if not projects:
    st.info("No projects found. Create a new project below.")
else:
    # إنشاء خريطة للتنقل بين الأسماء والـ IDs
    project_map = {f"{p['name']} (ID: {p['id']})": p for p in projects}
    options = list(project_map.keys())

    # معرفة الفهرس الحالي إن وجد
    current_selected_id = st.session_state.get("selected_project")
    default_index = 0

    if current_selected_id:
        for idx, (label, p_data) in enumerate(project_map.items()):
            if p_data["id"] == current_selected_id:
                default_index = idx
                break

    selected_option = st.selectbox(
        "Choose Project",
        options,
        index=default_index
    )

    selected_project_data = project_map[selected_option]

    # حفظ القيمة تلقائياً وفوراً في st.session_state
    st.session_state["selected_project"] = selected_project_data["id"]
    st.session_state["selected_project_name"] = selected_project_data["name"]


# ===========================
# Current Active Project Info & Navigation
# ===========================

active_id = st.session_state.get("selected_project")

if active_id:
    st.divider()
    active_name = st.session_state.get("selected_project_name", active_id)
    st.success(f"✅ Currently Active Project: **{active_name}** (`{active_id}`)")

    # جلب الـ Tenders الخاصة بالمشروع المحدّد
    try:
        tenders = get_tenders(active_id)
        st.session_state["tenders"] = tenders
        
        st.write(f"### Tenders in this project ({len(tenders)})")
        
        if tenders:
            # اختيار مناقصة محددة للتفاعل معها
            tender_map = {f"{t.get('tender_name', 'Untitled')} (ID: {t.get('id')})": t for t in tenders}
            selected_t_label = st.selectbox("Select a Tender to Work On", list(tender_map.keys()))
            chosen_tender = tender_map[selected_t_label]
            
            # حفظ الـ tender_id للـ Chat والـ Report
            st.session_state["tender_id"] = chosen_tender.get("id")
            st.session_state["tender_title"] = chosen_tender.get("tender_name")

            # أزرار الانتقال (Chat, Report, Upload)
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("💬 Open Chat", use_container_width=True):
                    st.switch_page("pages/Chat.py")
            with col2:
                if st.button("📊 View Report", use_container_width=True):
                    st.switch_page("pages/Report.py")
            with col3:
                if st.button("📤 Upload More Tenders", use_container_width=True):
                    st.switch_page("pages/Upload.py")

        else:
            st.info("No tenders uploaded for this project yet.")
            # زر الانتقال للرفع مباشرة عند عدم وجود مناقصات
            if st.button("📤 Upload First Tender", use_container_width=True):
                st.switch_page("pages/Upload.py")

    except Exception as e:
        st.error(f"Failed to load tenders: {e}")

st.divider()


# ===========================
# Create New Project
# ===========================

st.subheader("➕ Create New Project")

with st.form("create_project_form"):
    new_p_name = st.text_input("Project Name", placeholder="e.g. Saudi Tender Evaluation")
    new_p_desc = st.text_area("Description", placeholder="Optional description...")
    submit_button = st.form_submit_button("Create Project", use_container_width=True)

    if submit_button:
        if not new_p_name.strip():
            st.error("Project name cannot be empty.")
        else:
            try:
                created_p = create_project(name=new_p_name.strip(), description=new_p_desc.strip())
                new_id = created_p.get("id")
                
                st.session_state["selected_project"] = new_id
                st.session_state["selected_project_name"] = created_p.get("name", new_p_name)
                
                st.success(f"✅ Project '{new_p_name}' created successfully!")
                st.switch_page("pages/Upload.py")
            except Exception as err:
                st.error(f"❌ Failed to create project: {str(err)}")