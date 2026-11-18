from src.rag.ingestion.models import Chunk


class Chunker:
    def __init__(self, counter: int, max_tokers: int) -> None:
        pass

    def chunk_files(self) -> list[Chunk]:
        pass

    def chunk_file(self) -> list[Chunk]:
        pass

    def _count_tokens(self) -> None:
        pass

    def _split_to_long(self) -> list[Chunk]:
        pass

    def _fix_duplicate_is(self) -> None:
        pass


class PythonChunker:
    pass


class MarkdownChunker:
    pass


class CudaChunker:
    pass


class ConfigChunker:
    pass
