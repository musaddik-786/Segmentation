def chunk_documents(
    documents: list[dict],
    chunk_size: int = 1000,
    overlap: int = 200
) -> list[dict]:

    chunks = []

    for document in documents:
        text = document["text"]

        start = 0
        chunk_number = 1

        while start < len(text):

            end = start + chunk_size
            chunk_text = text[start:end]

            chunks.append({
                "source": document["source"],
                "page_number": document["page_number"],
                "chunk_number": chunk_number,
                "text": chunk_text
            })

            start += chunk_size - overlap
            chunk_number += 1

    return chunks



from loaders import load_pdf
from chunker import chunk_documents


PDF_PATH = r"/mnt/data/cedera-data/treaties/TRT-2026-001_Property_Quota_Share.pdf"


documents = load_pdf(PDF_PATH)

chunks = chunk_documents(documents)

print(f"Documents: {len(documents)}")
print(f"Chunks: {len(chunks)}")

for chunk in chunks[:5]:
    print("\n" + "=" * 80)
    print(f"Page: {chunk['page_number']}")
    print(f"Chunk: {chunk['chunk_number']}")
    print(chunk["text"][:500])
