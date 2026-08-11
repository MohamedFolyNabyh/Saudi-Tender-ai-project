# from qdrant_client import QdrantClient
# from qdrant_client.models import (
#     Distance,
#     VectorParams,
#     PointStruct
# )

# from app.core.config import settings


# class VectorService:

#     client = QdrantClient(
#         url=settings.QDRANT_URL,
#         prefer_grpc=True,
#         timeout=60.0
#     )

#     @classmethod
#     def create_collection(
#         cls,
#         collection_name,
#         vector_size
#     ):

#         collections = cls.client.get_collections().collections

#         if collection_name in [
#             c.name
#             for c in collections
#         ]:
#             return

#         cls.client.create_collection(
#             collection_name=collection_name,
#             vectors_config=VectorParams(
#                 size=vector_size,
#                 distance=Distance.COSINE
#             )
#         )

#     @classmethod
#     def upload(cls,collection_name,documents,embeddings,tender):

#         cls.create_collection(
#             collection_name,
#             len(embeddings[0])
#         )

#         points = []

#         for doc, vector in zip(
#             documents,
#             embeddings
#         ):

#             points.append(

#                 PointStruct(

#                     id=doc.metadata["id"],

#                     vector=vector.tolist(),

#                     payload={

#                         "id": doc.metadata["id"],
#                         "text": doc.page_content,
#                         "page": doc.metadata["page"],
#                         "source": tender.tender_name,
#                         "project_id": tender.project_id,
#                         "tender_id": tender.id

#                     }

#                 )

#             )

#         cls.client.upsert(
#             collection_name=collection_name,
#             points=points
#         )

#     @classmethod
#     def search(cls,collection_name, query_vector,limit:int =10):
#         print("Start Search")


#         results = cls.client.query_points(
#             collection_name=collection_name,
#             query=query_vector,
#             limit=limit
#         )
#         print("End Search")

#         return [
#             point.payload
#             for point in results.points
#         ]
#     @classmethod
#     def get_all_chunks(cls, collection_name: str, batch_size: int = 100) -> list[dict]:
#         """
#         جلب كل الـ Chunks من مجموعة Qdrant محددة باستخدام الـ Scrolling
#         """
#         all_chunks = []
#         offset = None

#         while True:
#             # استخدام client.scroll للسحب على دفعات (Pagination)
#             points, next_offset = cls.client.scroll(
#                 collection_name=collection_name,
#                 limit=batch_size,
#                 offset=offset,
#                 with_payload=True,
#                 with_vectors=False
#             )

#             # استخراج الـ Payload وإضافة id الخاص بالنقطة للتتبع
#             for point in points:
#                 if point.payload:
#                     chunk_data = dict(point.payload)
#                     chunk_data["point_id"] = point.id
#                     all_chunks.append(chunk_data)

#             # الخروج عند الوصول لنهاية الـ Collection
#             if next_offset is None:
#                 break

#             offset = next_offset

#         return all_chunks


from typing import Any, Dict, List, Optional
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from app.core.config import settings


class VectorService:
    client = QdrantClient(
        url=settings.QDRANT_URL,
        prefer_grpc=True,
        timeout=60.0,
    )

    @classmethod
    def create_collection(cls, collection_name: str, vector_size: int) -> None:
        collections = cls.client.get_collections().collections
        existing_names = [c.name for c in collections]

        if collection_name in existing_names:
            return

        cls.client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=vector_size,
                distance=Distance.COSINE,
            ),
        )

    @classmethod
    def upload(
        cls,
        collection_name: str,
        documents: List[Any],
        embeddings: List[Any],
        tender: Any,
    ) -> None:
        cls.create_collection(
            collection_name=collection_name,
            vector_size=len(embeddings[0]),
        )

        points = [
            PointStruct(
                id=doc.metadata["id"],
                vector=vector.tolist(),
                payload={
                    "id": doc.metadata["id"],
                    "text": doc.page_content,
                    "page": doc.metadata["page"],
                    "source": tender.tender_name,
                    "project_id": tender.project_id,
                    "tender_id": tender.id,
                },
            )
            for doc, vector in zip(documents, embeddings)
        ]

        cls.client.upsert(
            collection_name=collection_name,
            points=points,
        )

    @classmethod
    def search(
        cls,
        collection_name: str,
        query_vector: Any,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        print("Start Search")

        results = cls.client.query_points(
            collection_name=collection_name,
            query=query_vector.tolist(),
            limit=limit,
            with_payload=True,
            with_vectors=False,
        )

        print("End Search")

        return [
            {
                **(point.payload or {}),
                "score": point.score,
            }
            for point in results.points
        ]

    @classmethod
    def get_all_chunks(
        cls,
        collection_name: str,
        batch_size: int = 100,
    ) -> List[Dict[str, Any]]:
        all_chunks = []
        offset: Optional[Any] = None

        while True:
            points, next_offset = cls.client.scroll(
                collection_name=collection_name,
                limit=batch_size,
                offset=offset,
                with_payload=True,
                with_vectors=False,
            )

            for point in points:
                if point.payload:
                    chunk_data = dict(point.payload)
                    chunk_data["point_id"] = point.id
                    all_chunks.append(chunk_data)

            if next_offset is None:
                break

            offset = next_offset

        return all_chunks