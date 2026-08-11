from app.services.llm_service import LLMService
from app.services.rag_service import RAGService
from langsmith import traceable


class RiskService:

    @classmethod
    @traceable(name="Risk Analysis", run_type="chain")
    def analyze(
        cls,
        tender
    ):

        chunks = RAGService.retrieve(
            tender,
                """
                Find all information related to:

                - Risks
                - Penalties
                - Obligations
                - Financial Guarantees
                - Deadlines
                - Contract Termination
                """
            ,limit=20
        )

        context = "\n\n".join(
            chunk["text"]
            for chunk in chunks
        )

        prompt = f"""
You are a Saudi Tender Risk Analyst.

Analyze ONLY the provided tender context.

Rules:
- Do not use external knowledge.
- Do not invent facts, penalties, dates, amounts, or requirements.
- Every identified risk must be supported by the context.
- If information is missing, write: "Not specified in the tender."
- Keep all numbers, dates, percentages, and guarantees exactly as stated.
- Clearly separate tender facts from analyst recommendations.
- Write in English only.

Generate:

1. Financial Risks
2. Legal Risks
3. Technical Risks
4. Schedule Risks
5. Penalties
6. Critical Clauses
7. Overall Risk Rating
8. Recommendations

For each risk include:
- Description
- Evidence from tender
- Impact
- Risk Level

For Recommendations:
Only recommend actions based on identified risks.
Do not introduce new tender requirements.

Context:

{context}
"""

        answer = LLMService.generate(prompt)

        return {
            "answer": answer,
            "sources": [
                {
                    "page": c["page"],
                    "source": c["source"]
                }
                for c in chunks
            ]
        }