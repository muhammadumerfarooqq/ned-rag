from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter


def load_and_chunk(pdf_path: str, chunk_size: int = 1000, chunk_overlap: int = 150):
    """Load a PDF and split it into overlapping text chunks.

    Returns a list of chunk strings.
    """
    reader = PdfReader(pdf_path)
    full_text = ""
    for page in reader.pages:
        full_text += page.extract_text()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    return splitter.split_text(full_text)


# This block runs ONLY when you execute this file directly,
# NOT when another file imports load_and_chunk from it.
if __name__ == "__main__":
    chunks = load_and_chunk("data/regulations_4155.pdf")
    print(f"Loaded and chunked into {len(chunks)} chunks.")
    print(f"First chunk preview:\n{chunks[0][:200]}")