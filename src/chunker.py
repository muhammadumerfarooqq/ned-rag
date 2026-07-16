from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter

# --- single source of truth for chunking config ---
# Clause-aware splitting: break at clause numbers (7.5, 8.1, 12.1) before
# falling back to paragraphs/lines. Selected in Phase 10 — raised recall@1
# from 0.478 to 0.652 and recall@5 from 0.957 to 1.000 vs pure character
# splitting, without the neighbour-collision seen at chunk_size=500.
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150
SEPARATORS = [r"\n\s*\d+\.\d+", "\n\n", "\n", " ", ""]
IS_SEPARATOR_REGEX = True


def load_and_chunk(pdf_path: str, chunk_size: int = CHUNK_SIZE, chunk_overlap: int = CHUNK_OVERLAP):
    """Load a PDF and split it into overlapping text chunks.

    Returns a list of chunk strings.
    """
    reader = PdfReader(pdf_path)
    full_text = ""
    for page in reader.pages:
        full_text += page.extract_text()

    kwargs = {"chunk_size": chunk_size, "chunk_overlap": chunk_overlap}
    if SEPARATORS is not None:
        kwargs["separators"] = SEPARATORS
        kwargs["is_separator_regex"] = IS_SEPARATOR_REGEX

    splitter = RecursiveCharacterTextSplitter(**kwargs)
    return splitter.split_text(full_text)


if __name__ == "__main__":
    chunks = load_and_chunk("data/regulations_4155.pdf")
    print(f"Loaded and chunked into {len(chunks)} chunks.")
    print(f"First chunk preview:\n{chunks[0][:200]}")