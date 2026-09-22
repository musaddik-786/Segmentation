import re


ARTICLE_PATTERN = re.compile(
    r"^\s*ARTICLE\s+(\d+[A-Z]?)\s*(?:—|-)?\s*(.*)$",
    re.IGNORECASE
)

CLAUSE_PATTERN = re.compile(
    r"^\s*((?:\d+\([a-z]\))|(?:\d+(?:\.\d+)+))\s+(.*)$",
    re.IGNORECASE
)


def clause_aware_chunk_documents(documents: list[dict]) -> list[dict]:
    chunks = []

    current_article = None
    chunk_number = 1

    for document in documents:
        text = document["text"]

        lines = text.splitlines()

        current_clause_lines = []
        current_clause_ref = None

        def flush_clause():
            nonlocal current_clause_lines
            nonlocal current_clause_ref
            nonlocal chunk_number

            if not current_clause_lines:
                return

            clause_text = "\n".join(current_clause_lines).strip()

            if not clause_text:
                current_clause_lines = []
                current_clause_ref = None
                return

            chunks.append({
                "source": document["source"],
                "page_number": document["page_number"],
                "chunk_number": chunk_number,
                "article": current_article,
                "clause_ref": current_clause_ref,
                "text": clause_text
            })

            chunk_number += 1

            current_clause_lines = []
            current_clause_ref = None

        for line in lines:
            stripped = line.strip()

            if not stripped:
                continue

            # ---------------------------------
            # ARTICLE
            # ---------------------------------
            article_match = ARTICLE_PATTERN.match(stripped)

            if article_match:
                flush_clause()

                article_number = article_match.group(1)

                current_article = f"ARTICLE {article_number}"

                continue

            # ---------------------------------
            # CLAUSE
            # ---------------------------------
            clause_match = CLAUSE_PATTERN.match(stripped)

            if clause_match:
                flush_clause()

                current_clause_ref = clause_match.group(1)

                current_clause_lines = [stripped]

                continue

            # ---------------------------------
            # CONTINUATION OF CURRENT CLAUSE
            # ---------------------------------
            if current_clause_lines:
                current_clause_lines.append(stripped)

            else:
                # Text before the first recognised
                # clause/article.
                chunks.append({
                    "source": document["source"],
                    "page_number": document["page_number"],
                    "chunk_number": chunk_number,
                    "article": current_article,
                    "clause_ref": None,
                    "text": stripped
                })

                chunk_number += 1

        flush_clause()

    return chunks



from loaders import load_pdf
from clause_chunker import clause_aware_chunk_documents


PDF_PATH = r"/mnt/data/cedera-data/treaties/TRT-2026-001_Property_Quota_Share.pdf"


documents = load_pdf(PDF_PATH)

chunks = clause_aware_chunk_documents(documents)

print(f"Documents: {len(documents)}")
print(f"Clause-aware chunks: {len(chunks)}")


for chunk in chunks:
    print("\n" + "=" * 80)
    print(f"Page: {chunk['page_number']}")
    print(f"Chunk: {chunk['chunk_number']}")
    print(f"Article: {chunk['article']}")
    print(f"Clause: {chunk['clause_ref']}")
    print("-" * 80)
    print(chunk["text"][:1000])
