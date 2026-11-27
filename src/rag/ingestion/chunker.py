from src.rag.ingestion.tokenizer import TokenCounter
from src.rag.ingestion.models import (Chunk,
                                      SourceFile,
                                      FileType)


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
        self.python = PythonChunker()
        self.markdown = MarkdownChunker()
        self.cuda = CudaChunker()
        self.config = ConfigChunker()

    def chunk_files(self, files: list[SourceFile]) -> list[Chunk]:
        chunks: list[Chunk] = []
        rework_chunks: list[Chunk] = []
        for file in files:
            try:
                chunks.extend(self.chunk_file(file=file))
            except Exception as e:
                print(f"Warning on {file.source} > {e}")
        self._count_tokens(chunks=chunks)
        for chunk in chunks:
            if chunk.n_tokens > self.max_tokens:
                rework_chunks.extend(self._split_too_long(chunk=chunk))
            else:
                rework_chunks.append(chunk)
        self._fix_duplicate_ids(chunks=rework_chunks)
        return rework_chunks

    def chunk_file(self, file: SourceFile) -> list[Chunk]:
        match file.type:
            case FileType.CODE_PYTHON:
                return self.python.chunking(file=file)
            case FileType.DOC_MARKDOWN:
                return self.markdown.chunking(file=file)
            case FileType.CODE_CUDA:
                return self.cuda.chunking(file=file)
            case FileType.CONFIG:
                return self.config.chunking(file=file)
            case _:
                print(f"IGNORED FILE: {file.source}")
                return []

    def _count_tokens(self, chunks: list[Chunk]) -> None:
        if not chunks:
            return
        tokens_list = self.counter.count_batch(
            texts=[chunk.content for chunk in chunks]
            )
        for chunk, n in zip(chunks, tokens_list, strict=True):
            chunk.n_tokens = n

    def _split_too_long(self, chunk: Chunk) -> list[Chunk]:
        chunks: list[Chunk] = []
        tot_token = 0
        content_in = ""
        stock_start = 0
        part = 1
        contents = chunk.content.splitlines(keepends=True)
        all_tokens = self.counter.count_batch(contents)
        for i, tmp in enumerate(zip(contents, all_tokens)):
            content, nb_token = tmp
            if tot_token + nb_token <= self.max_tokens:
                tot_token += nb_token
                content_in += content
            else:
                if content_in != "":
                    chunks.append(chunk.model_copy(
                        update={
                            "start_line": chunk.start_line + stock_start,
                            "end_line": chunk.start_line + i - 1,
                            "n_tokens": tot_token,
                            "content": content_in,
                            "symbol": (f"{chunk.symbol} (part {part})")
                            if chunk.symbol
                            else (f"{chunk.chunk_id} (part {part})"),
                            "parent": chunk.symbol if chunk.symbol
                            else chunk.chunk_id
                        }
                    ))
                    part += 1
                stock_start = i
                content_in = content
                tot_token = nb_token
        chunks.append(chunk.model_copy(
            update={
                "start_line": chunk.start_line + stock_start,
                "end_line": chunk.start_line + i,
                "n_tokens": tot_token,
                "content": content_in,
                "symbol": (f"{chunk.symbol} (part {part})")
                if chunk.symbol else (f"{chunk.chunk_id} (part {part})"),
                "parent": chunk.symbol if chunk.symbol else chunk.chunk_id
            }
        ))
        return chunks

    def _fix_duplicate_ids(self, chunks: list[Chunk]) -> None:
        counters: dict[str, int] = dict()
        seen: set[str] = set()
        for chunk in chunks:
            if chunk.chunk_id not in seen:
                seen.add(chunk.chunk_id)
                continue
            base = chunk.chunk_id
            n = counters.get(base, 1)
            new_id = f"{base}#{n}"
            while new_id in seen:
                n += 1
                new_id = f"{base}#{n}"
            chunk.chunk_id = new_id
            counters[base] = n + 1
            seen.add(new_id)


class PythonChunker:
    def chunking(self, file: SourceFile) -> list[Chunk]:
        pass


class MarkdownChunker:
    def chunking(self, file: SourceFile) -> list[Chunk]:
        pass


class CudaChunker:
    def chunking(self, file: SourceFile) -> list[Chunk]:
        pass


class ConfigChunker:
    def chunking(self, file: SourceFile) -> list[Chunk]:
        pass
