import re


ARTICLE_PATTERN = re.compile(
    r"^\s*ARTICLE\s+\d+[A-Z]?(?:\s*[—-].*)?\s*$",
    re.IGNORECASE
)

CLAUSE_PATTERN = re.compile(
    r"^\s*(\d+\([a-z]\)|\d+\.\d+(?:\.\d+)*)\s+[A-Za-z]",
    re.IGNORECASE
)

SCHEDULE_PATTERN = re.compile(
    r"^\s*SCHEDULE\s+[A-Z0-9]+(?:\s*[—-].*)?\s*$",
    re.IGNORECASE
)


def is_pdf_header_footer(line: str) -> bool:

    line = line.strip()

    if not line:
        return False

    # Page number
    if re.fullmatch(r"Page\s+\d+", line, re.IGNORECASE):
        return True

    # Synthetic document notice
    if line.startswith("Synthetic document generated"):
        return True

    # Repeated treaty reference in PDF header
    if re.fullmatch(r"TRT-\d{4}-\d{3}", line):
        return True

    # Repeated treaty title in PDF header
    if line.endswith("Reinsurance Agreement"):
        return True

    return False


def chunk_documents(documents: list[dict]):

    chunks = []

    current_lines = []
    current_article = None
    current_clause = None

    chunk_number = 1
    current_page = None

    def save_chunk():

        nonlocal current_lines
        nonlocal chunk_number
        nonlocal current_clause

        if not current_lines:
            return

        text = "\n".join(current_lines).strip()

        if not text:
            current_lines = []
            return

        chunks.append({
            "source": documents[0]["source"],
            "page_number": current_page,
            "chunk_number": chunk_number,
            "article": current_article,
            "clause_ref": current_clause,
            "text": text
        })

        chunk_number += 1
        current_lines = []

    for document in documents:

        current_page = document["page_number"]

        lines = document["text"].splitlines()

        for line in lines:

            line = line.strip()

            if not line:
                continue

            # -----------------------------------------
            # Remove PDF headers / footers
            # -----------------------------------------

            if is_pdf_header_footer(line):
                continue

            # -----------------------------------------
            # ARTICLE
            # -----------------------------------------

            if ARTICLE_PATTERN.match(line):

                save_chunk()

                current_article = line
                current_clause = None

                current_lines.append(line)

                continue

            # -----------------------------------------
            # SCHEDULE
            # -----------------------------------------

            if SCHEDULE_PATTERN.match(line):

                save_chunk()

                current_article = line
                current_clause = None

                current_lines.append(line)

                continue

            # -----------------------------------------
            # CLAUSE
            # -----------------------------------------

            clause_match = CLAUSE_PATTERN.match(line)

            if clause_match:

                save_chunk()

                current_clause = clause_match.group(1)

                current_lines.append(line)

                continue

            # -----------------------------------------
            # NORMAL TEXT / CONTINUATION
            # -----------------------------------------

            current_lines.append(line)

    # Save final chunk
    save_chunk()

    return chunks
