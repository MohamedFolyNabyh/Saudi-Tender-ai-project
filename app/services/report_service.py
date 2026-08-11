from app.services.rag_service import RAGService
from app.services.llm_service import LLMService
from langsmith import traceable

class ReportService:

    @classmethod
    @traceable(name="Executive Report", run_type="chain")
    def generate(
        cls,
        tender,
        history=None
    ):

        chunks = RAGService.retrieve(
            tender,
            """
Retrieve information required to build an executive tender report, including:
tender overview, objective, scope of work, technical requirements,
required documents, important dates, evaluation criteria,
financial and contractual conditions, guarantees, penalties,
compliance obligations, and risks.
"""
        )

        context = "\n\n".join(
            chunk["text"]
            for chunk in chunks
        )

        prompt = f"""
You are an expert Saudi Tender Analyst.

Generate a professional Executive Summary using ONLY the provided tender context.

Rules:

* Do not use external knowledge or assumptions.
* Do not hallucinate.
* If information is missing, write: "Not specified in the tender."
* Preserve dates, numbers, percentages, guarantees, and monetary values exactly.
* Write in English only. Translate Arabic terms accurately.
* Clearly distinguish tender requirements from identified risks.

Include:

1. Tender Overview
2. Objective & Scope of Work
3. Technical Requirements
4. Required Documents
5. Important Dates
6. Evaluation Criteria
7. Key Risks
8. Financial & Contractual Requirements
9. Executive Assessment
10. Final Recommendation

Use clear headings and bullet points.

Tender Context:
{context}

"""

        answer = LLMService.generate(prompt,task_type="analysis")

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