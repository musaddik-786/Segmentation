import os

from dotenv import load_dotenv
from langchain_openai import AzureOpenAIEmbeddings

load_dotenv()


def get_embeddings():
    return AzureOpenAIEmbeddings(
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
        azure_deployment=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT"),
    )



from loaders import load_pdf
from chunker import chunk_documents
from embedder import get_embeddings


PDF_PATH = r"/mnt/data/cedera-data/treaties/TRT-2026-001_Property_Quota_Share.pdf"


documents = load_pdf(PDF_PATH)

chunks = chunk_documents(documents)

embeddings = get_embeddings()

texts = [chunk["text"] for chunk in chunks]

vectors = embeddings.embed_documents(texts)

print(f"Chunks: {len(chunks)}")
print(f"Embeddings: {len(vectors)}")
print(f"Vector dimensions: {len(vectors[0])}")



