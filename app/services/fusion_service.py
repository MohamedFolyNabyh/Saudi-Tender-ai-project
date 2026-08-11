class FusionService:

    @staticmethod
    def rrf(
        bm25_results,
        vector_results,
        k=60
    ):

        scores = {}
        documents = {}

        # BM25
        for rank, item in enumerate(bm25_results):

            doc = item["document"]

            key = (
                doc["page"],
                doc["text"]
            )

            documents[key] = doc

            scores[key] = scores.get(
                key,
                0
            ) + 1 / (k + rank + 1)

        # Vector Search
        for rank, doc in enumerate(vector_results):

            key = (
                doc["page"],
                doc["text"]
            )

            documents[key] = doc

            scores[key] = scores.get(
                key,
                0
            ) + 1 / (k + rank + 1)

        ranked = sorted(
            documents.values(),
            key=lambda d: scores[
                (
                    d["page"],
                    d["text"]
                )
            ],
            reverse=True
        )

        return ranked