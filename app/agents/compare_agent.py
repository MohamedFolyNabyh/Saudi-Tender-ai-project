from app.services.compare_service import CompareService


class CompareAgent:

    @staticmethod
    def run(state):

        result = CompareService.compare(

            state["tender1"],

            state["tender2"]

        )

        state["answer"] = result["answer"]

        return state