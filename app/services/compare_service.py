
from app.services.rag_service import RAGService
from app.services.llm_service import LLMService


class CompareService:

    @classmethod
    def compare(
        cls,
        tender1,
        tender2
    ):

        # =========================
        # Retrieve Tender A
        # =========================

        context1_chunks = RAGService.retrieve(
            tender=tender1,
            question="""
            Extract important tender information:

            - Scope of Work
            - Technical Requirements
            - Financial Requirements
            - Deadlines
            - Evaluation Criteria
            - Penalties
            - Risks
            """
        )

        # =========================
        # Retrieve Tender B
        # =========================

        context2_chunks = RAGService.retrieve(
            tender=tender2,
            question="""
            Extract important tender information:

            - Scope of Work
            - Technical Requirements
            - Financial Requirements
            - Deadlines
            - Evaluation Criteria
            - Penalties
            - Risks
            """
        )

        # =========================
        # Build Context
        # =========================

        context1 = "\n\n".join(
            chunk["text"]
            for chunk in context1_chunks
        )

        context2 = "\n\n".join(
            chunk["text"]
            for chunk in context2_chunks
        )

        # =========================
        # Comparison Prompt
        # =========================

        prompt = f"""
You are a Senior Tender Consultant.

Compare two Saudi tender documents.

Tender A:

{context1}

---

Tender B:

{context2}

---

Generate a professional comparison report.

Include:

1. Executive Summary

2. Scope of Work Comparison

3. Technical Requirements Comparison

4. Financial Requirements Comparison

5. Timeline Comparison

6. Evaluation Criteria Comparison

7. Risk Comparison

8. Advantages of Tender A

9. Advantages of Tender B

10. Final Recommendation

Use tables when useful.

Important rules:

- Only use information provided in the tender contexts.
- Do not hallucinate.
- If information is missing, explicitly state that it was not found.
- Clearly distinguish Tender A from Tender B.
"""

        # =========================
        # Generate Answer
        # =========================

        answer = LLMService.generate(
            prompt,
            task_type="analysis"
        )

        # =========================
        # Return Result
        # =========================

        return {
            "answer": answer,

            "sources": [
                {
                    "tender": "Tender A",
                    "page": chunk["page"],
                    "source": chunk["source"]
                }
                for chunk in context1_chunks
            ]
            +
            [
                {
                    "tender": "Tender B",
                    "page": chunk["page"],
                    "source": chunk["source"]
                }
                for chunk in context2_chunks
            ]
        }
