from embedder import get_embeddings
from chroma_store import get_chroma_collection


QUERY = "Article 4(b) flood exclusion"


embeddings_model = get_embeddings()
collection = get_chroma_collection()

query_vector = embeddings_model.embed_query(QUERY)

results = collection.query(
    query_embeddings=[query_vector],
    n_results=5
)


for i, document in enumerate(results["documents"][0]):
    metadata = results["metadatas"][0][i]
    distance = results["distances"][0][i]

    print("\n" + "=" * 80)
    print(f"Result: {i + 1}")
    print(f"Distance: {distance}")
    print(f"Page: {metadata['page_number']}")
    print(f"Chunk: {metadata['chunk_number']}")
    print(f"Treaty: {metadata['treaty_ref']}")
    print("\n" + document)
