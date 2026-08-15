from sqlalchemy.orm import Session
from app.database.models.project import Project
from app.database.models.tender import Tender
from app.database.models.user import User
from app.graph.state import GraphState


class SQLAgent:

    @classmethod
    def run(cls, state: GraphState) -> dict:
        question = state.get("question", "")
        db: Session = state.get("db")
        current_user = state.get("current_user")

        if not db:
            return {"answer": "Database session is missing from state."}

        q = question.lower()
        answer = ""

        # استعلام مصفى لمناقصات المستخدم الحالي عبر العلاقة مع Project
        user_tenders_query = (
            db.query(Tender)
            .join(Tender.project)
            .filter(Project.user_id == current_user.id)
        )

        # 1. عدد المناقصات الخاصة بالمستخدم
        if any(k in q for k in ["how many tender", "number of tender", "count tender", "tender count", "عدد المناقص"]):
            count = user_tenders_query.count()
            answer = f"You have {count} tender(s) in your projects."

        # 2. عدد المشاريع الخاصة بالمستخدم
        elif any(k in q for k in ["how many project", "number of project", "count project", "project count", "عدد المشاريع"]):
            user_projects_count = (
                db.query(Project)
                .filter(Project.user_id == current_user.id)
                .count()
            )
            answer = f"You have {user_projects_count} project(s)."

        # 3. قائمة المناقصات الخاصة بالمستخدم
        elif any(k in q for k in ["list all tenders", "show all tenders", "list tenders", "show tenders", "all tenders", "كل المناقص", "المناقصات"]):
            tenders = user_tenders_query.all()
            if not tenders:
                answer = "No tenders found for your account."
            else:
                answer = "\n".join(f"- {t.tender_name}" for t in tenders)

        # 4. قائمة المشاريع الخاصة بالمستخدم
        elif any(k in q for k in ["list all projects", "show all projects", "list projects", "show projects", "all projects", "كل المشاريع", "المشاريع"]):
            projects = (
                db.query(Project)
                .filter(Project.user_id == current_user.id)
                .all()
            )
            if not projects:
                answer = "No projects found for your account."
            else:
                answer = "\n".join(f"- {p.name}" for p in projects)

        # 5. حالات المناقصات
        elif any(k in q for k in ["status", "tender statuses", "حالة", "حالات"]):
            tenders = user_tenders_query.all()
            if not tenders:
                answer = "No tenders found for your account."
            else:
                answer = "\n".join(
                    f"- {t.tender_name}: {getattr(t.status, 'value', t.status)}"
                    for t in tenders
                )

        # 6. معلومات المستخدمين
        elif any(k in q for k in ["how many users", "number of users", "count users", "عدد المستخدمين"]):
            user_count = db.query(User).count()
            answer = f"There are {user_count} registered user(s) in the system."

        # 7. رد افتراضي إذا لم يتم التعرف على الاستعلام بالضبط
        else:
            answer = "I could not determine a suitable database query for this question."

        return {"answer": answer}