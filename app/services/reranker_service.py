from sentence_transformers import CrossEncoder


class RerankerService:

    model = CrossEncoder(
        "BAAI/bge-reranker-base"
    )

    @classmethod
    def rerank(cls,question: str,documents: list,top_k: int = 5):

        pairs = [

            (
                question,
                doc["text"]
            )

            for doc in documents

        ]

        scores = cls.model.predict(pairs)

        ranked = sorted(

            zip(documents, scores),

            key=lambda x: x[1],

            reverse=True

        )

        return [

            doc

            for doc, _ in ranked[:top_k]

        ]
        # ranked[:top_k]
