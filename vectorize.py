from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os

# --- Configuration ---
PDF_DIRECTORY = "my_pdfs"
VECTOR_STORE_PATH = "chroma_db"
EMBEDDING_MODEL = "sentence-transformers/all-mpnet-base-v2"


def vectorize_pdfs():
    """
    Processes all PDFs in the specified directory, splits them into chunks,
    and stores their embeddings in a Chroma vector store.
    """
    print("Starting PDF vectorization...")
    documents = []
    for filename in os.listdir(PDF_DIRECTORY):
        if filename.endswith(".pdf"):
            path = os.path.join(PDF_DIRECTORY, filename)
            loader = PyPDFLoader(path)
            documents.extend(loader.load())

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(documents)

    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

    vectorstore = Chroma.from_documents(
        documents=splits,
        embedding=embeddings,
        persist_directory=VECTOR_STORE_PATH
    )

    print(f"Vectorization complete. Vector store created at: {VECTOR_STORE_PATH}")

if __name__ == "__main__":
    vectorize_pdfs()
