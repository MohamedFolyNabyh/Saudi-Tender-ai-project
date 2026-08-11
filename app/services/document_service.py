import fitz

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


class DocumentService:

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    @staticmethod
    def load_pdf(pdf_path: str):

        pdf = fitz.open(pdf_path)

        documents = []

        for page_number, page in enumerate(pdf):

            documents.append(
                Document(
                    page_content=page.get_text(),
                    metadata={
                        "page": page_number + 1
                    }
                )
            )

        pdf.close()

        return documents

    @classmethod
    def split_pdf(cls, pdf_path: str):

        chunks = cls.splitter.split_documents(
            cls.load_pdf(pdf_path)
        )

        for idx, chunk in enumerate(chunks):
            chunk.metadata["id"] = idx

        return chunks