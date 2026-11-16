from pydantic import BaseModel, Field
from enum import StrEnum


class FileType(StrEnum):
    CODE_PYTHON = "code_python"
    CODE_CUDA = "code_cuda"
    DOC_MARKDOWN = "doc_markdown"
    CONFIG = "config"
    OTHER = "other"


class ReasonType(StrEnum):
    BUILD_ARTIFACT = "build_artifact"
    VENDORED = "vendored"
    TEST_DIR = "test_dir"
    TOO_LARGE = "too_large"
    BINARY = "binary"
    ENCODING = "encoding"
    EMPTY = "empty"
    TRIVIAL_INIT = "trivial_init"


class SourceFile(BaseModel):
    source: str
    type: FileType
    language: str
    top_dir: str
    is_test: bool
    size_bytes: int
    n_lines: int
    n_tokens: int = 0
    content: str = Field(default="", exclude=True, repr=False)


class ExcludedFile(BaseModel):
    source: str
    reason: ReasonType


class Chunk(BaseModel):
    chunk_id: str
    source: str
    type: FileType
    language: str
    symbol: str | None
    kind: str
    start_line: int
    end_line: int
    parent: str | None
    imports: list[str]
    top_dir: str
    is_test: bool
    n_tokens: int
    content: str
