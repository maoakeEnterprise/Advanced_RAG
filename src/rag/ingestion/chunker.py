from src.rag.ingestion.tokenizer import TokenCounter
from src.rag.ingestion.models import (Chunk,
                                      SourceFile)


def make_chunk(file: SourceFile,
               start_line: int,
               end_line: int,
               content: str,
               kind: str,
               imports: list[str],
               symbol: str | None = None,
               parent: str | None = None,
               ) -> Chunk:
    if symbol and parent:
        chunk_id = f"{file.source}::{parent}.{symbol}"
    elif symbol:
        chunk_id = f"{file.source}::{symbol}"
    else:
        chunk_id = f"{file.source}::L{start_line}-L{end_line}"
    return Chunk(
        chunk_id=chunk_id,
        source=file.source,
        type=file.type,
        language=file.language,
        kind=kind,
        start_line=start_line,
        end_line=end_line,
        parent=parent,
        imports=imports,
        top_dir=file.top_dir,
        is_test=file.is_test,
        n_tokens=0,
        content=content,
        symbol=symbol
    )


class Chunker:
    def __init__(self, counter: TokenCounter, max_tokens: int = 800) -> None:
        self.counter = counter
        self.max_tokens = max_tokens

    def chunk_files(self, files: list[SourceFile]) -> list[Chunk]:
        chunks: list[Chunk] = []
        for file in files:
            chunks.extend(self.chunk_file(file=file))
            n_tokens = self._count_tokens(chunks)
            if n_tokens > self.max_tokens:
                pass

    def chunk_file(self, file: SourceFile) -> list[Chunk]:
        pass

    def _count_tokens(self, chunks: list[Chunk]) -> int:
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
