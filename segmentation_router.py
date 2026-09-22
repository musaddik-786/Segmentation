from loaders import load_pdf


PDF_PATH = r"/mnt/data/cedera-data/treaties/TRT-2026-003_Property_Catastrophe_XoL.pdf"


documents = load_pdf(PDF_PATH)

print(f"Pages: {len(documents)}")

for document in documents[:3]:
    print("\n" + "=" * 80)
    print(f"Page: {document['page_number']}")
    print(document["text"][:1000])
