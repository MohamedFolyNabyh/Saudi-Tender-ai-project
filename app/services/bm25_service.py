

from rank_bm25 import BM25Okapi
import re


class BM25Service:

    @staticmethod
    def tokenize(text: str):

        return re.findall(r"\w+", text.lower())


    @classmethod
    def search(cls,chunks,
    question,
        top_k=20
    ):

        corpus = [
            cls.tokenize(chunk["text"])
            for chunk in chunks
        ]

        bm25 = BM25Okapi(corpus)

        query = cls.tokenize(question)

        scores = bm25.get_scores(query)

        ranked = sorted(
            zip(chunks, scores),
            key=lambda x: x[1],
            reverse=True
        )

        return [
            {
                "document": chunk,
                "score": float(score)
            }
            for chunk, score in ranked[:top_k]
        ]