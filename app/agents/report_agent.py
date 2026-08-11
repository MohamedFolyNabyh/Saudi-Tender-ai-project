from app.services.report_service import ReportService


class ReportAgent:

    @staticmethod
    def run(state):

        result = ReportService.generate(

            tender=state["tender"],

            history=state["history"]

        )

        state["answer"] = result["answer"]

        state["sources"] = result["sources"]

        return state