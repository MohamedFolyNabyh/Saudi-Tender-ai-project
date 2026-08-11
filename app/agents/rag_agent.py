from app.services.rag_service import RAGService


class RAGAgent:

    @staticmethod
    def run(state):
        print(">>>> Risk Agent")

        result = RAGService.ask(

            tender=state["tender"],

            question=state["question"],

            history=state["history"]

        )


        state["answer"] = result["answer"]

        state["sources"] = result["sources"]

        return state