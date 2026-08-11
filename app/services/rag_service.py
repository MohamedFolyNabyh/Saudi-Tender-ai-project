from app.database.models.tender import Tender

from app.services.embedding_service import EmbeddingService
from app.services.vector_service import VectorService
from app.services.bm25_service import BM25Service
from app.services.fusion_service import FusionService
from app.services.reranker_service import RerankerService
from app.services.llm_service import LLMService
from langsmith import traceable


class RAGService:
    
    @classmethod
    @traceable(name="Retrieve", run_type="retriever")
    def retrieve( cls,tender: Tender, question: str, limit: int = 5):
        embedding = EmbeddingService.model.encode(question,normalize_embeddings=True)

        vector_results = VectorService.search(collection_name=tender.qdrant_collection,
        query_vector=embedding.tolist(),
        limit=50
         )

        bm25_results = BM25Service.search(
        vector_results,
        question
        )

        merged = FusionService.rrf(bm25_results,vector_results)

        reranked = RerankerService.rerank(question,merged)

        return reranked[:limit]
        

    @classmethod
    @traceable(name="RAG Generation", run_type="chain")
    def ask(
        cls,
        tender: Tender,
        question: str,
        history: list | None = None
    ):

        chunks = cls.retrieve(
            tender=tender,
            question=question
        )

        context = "\n\n".join(
            chunk["text"]
            for chunk in chunks
        )

        history_text = ""

        if history:
            history_text = "\n".join(
                f"{msg['role']}: {msg['content']}"
                for msg in history
            )

        prompt = f"""
You are an AI assistant specialized in Saudi Tender Analysis.

Rules:
- Answer ONLY from the provided context.
- If the answer does not exist, say:
"I couldn't find this information in the tender."
- Do not hallucinate.

Conversation History:

{history_text}

Tender Context:

{context}

User Question:

{question}
"""

        answer = LLMService.generate(prompt,task_type="analysis")

        return {
            "answer": answer,
            "sources": [
                {
                    "page": chunk["page"],
                    "source": chunk["source"]
                }
                for chunk in chunks
            ]
        }