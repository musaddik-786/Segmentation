import chromadb


CHROMA_PATH = "./chroma_db"


def get_chroma_collection():
    client = chromadb.PersistentClient(path=CHROMA_PATH)

    collection = client.get_or_create_collection(
        name="treaty_clauses"
    )

    return collection



from loaders import load_pdf
from chunker import chunk_documents
from embedder import get_embeddings
from chroma_store import get_chroma_collection


PDF_PATH = r"/mnt/data/cedera-data/treaties/TRT-2026-001_Property_Quota_Share.pdf"


documents = load_pdf(PDF_PATH)

chunks = chunk_documents(documents)

embeddings_model = get_embeddings()

texts = [chunk["text"] for chunk in chunks]

vectors = embeddings_model.embed_documents(texts)

collection = get_chroma_collection()

ids = []
metadatas = []

for index, chunk in enumerate(chunks):
    ids.append(
        f"{chunk['source']}_page_{chunk['page_number']}_chunk_{chunk['chunk_number']}"
    )

    metadatas.append({
        "source": chunk["source"],
        "page_number": chunk["page_number"],
        "chunk_number": chunk["chunk_number"],
        "treaty_ref": "TRT-2026-001"
    })


collection.upsert(
    ids=ids,
    documents=texts,
    embeddings=vectors,
    metadatas=metadatas
)


print(f"Stored {len(ids)} chunks in Chroma")
print(f"Collection count: {collection.count()}")
