from sentence_transformers import SentenceTransformer


class EmbeddingService:

    model = SentenceTransformer(
        "BAAI/bge-m3"
    )

    @classmethod
    def embed_documents(cls, documents):

        texts = [
            doc.page_content
            for doc in documents
        ]

        embeddings = cls.model.encode(
            texts,
            normalize_embeddings=True
        )

        return embeddings

    @classmethod
    def embed_query(cls, query: str):

        embedding = cls.model.encode(
            query,
            normalize_embeddings=True
        )

        return embedding