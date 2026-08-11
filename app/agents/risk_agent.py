from app.services.risk_service import RiskService


class RiskAgent:

    @staticmethod
    def run(state):
        print(">>>> Risk Agent")

        result = RiskService.analyze(
            state["tender"]
        )

        state["answer"] = result["answer"]

        state["sources"] = result["sources"]

        return state