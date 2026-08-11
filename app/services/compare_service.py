from google import genai

from app.core.config import settings
from app.services.rag_service import RAGService


client = genai.Client(
    api_key=settings.GEMINI_API_KEY
)


class CompareService:


    @classmethod
    def compare(
        cls,
        tender1,
        tender2
    ):

        context1_chunks = RAGService.retrieve(
            tender1,
            """
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


        context2_chunks = RAGService.retrieve(
            tender2,
            """
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


        context1 = "\n\n".join(
            chunk["text"]
            for chunk in context1_chunks
        )


        context2 = "\n\n".join(
            chunk["text"]
            for chunk in context2_chunks
        )


        prompt = f"""

You are a Senior Tender Consultant.

Compare two tender documents.

Tender A:

{context1}


--------------------------------


Tender B:

{context2}


--------------------------------


Generate a professional comparison report.


Include:

1. Executive Summary


2. Scope Comparison


3. Technical Requirements Comparison


4. Financial Requirements Comparison


5. Timeline Comparison


6. Evaluation Criteria Comparison


7. Risk Comparison


8. Advantages of Tender A


9. Advantages of Tender B


10. Final Recommendation


Create tables when useful.

Only use provided information.

"""


        response = client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=prompt
        )


        return {

            "answer": response.text,

            "sources": [

                {
                    "tender": "Tender A",
                    "page": c["page"],
                    "source": c["source"]
                }

                for c in context1_chunks

            ]
            +
            [

                {
                    "tender": "Tender B",
                    "page": c["page"],
                    "source": c["source"]
                }

                for c in context2_chunks

            ]

        }