from pathlib import Path
import ast
from types import EllipsisType
from src.rag.ingestion.models import (SourceFile,
                                      ExcludedFile,
                                      FileType)


SNIFF_SIZE = 8000

EXCLUDED = {
    "build_artifact": frozenset({
        ".git",
        "__pycache__",
        "node_modules",
        ".venv",
        "build",
        "dist",
        ".tox",
        ".mypy_cache"
        }),
    "vendored": frozenset({
        "third_party",
        "vendor",
        "vendored",
        "external",
        "extern",
        "3rdparty"
    }),
    "test_dir": frozenset({
        "fixtures",
        "testdata",
        "test_data"
    })
}
# Extension (lowercase) -> (type, language)
EXTENSIONS: dict[str, tuple[FileType, str]] = {
    # Python
    ".py": (FileType.CODE_PYTHON, "python"),
    ".pyi": (FileType.CODE_PYTHON, "python"),
    # CUDA
    ".cu": (FileType.CODE_CUDA, "cuda"),
    ".cuh": (FileType.CODE_CUDA, "cuda"),
    # C / C++ (grouped with CUDA: native kernels)
    ".cpp": (FileType.CODE_CUDA, "cpp"),
    ".cc": (FileType.CODE_CUDA, "cpp"),
    ".h": (FileType.CODE_CUDA, "cpp"),
    ".hpp": (FileType.CODE_CUDA, "cpp"),
    ".inl": (FileType.CODE_CUDA, "cpp"),
    # Documentation
    ".md": (FileType.DOC_MARKDOWN, "markdown"),
    ".markdown": (FileType.DOC_MARKDOWN, "markdown"),
    ".rst": (FileType.DOC_MARKDOWN, "restructuredtext"),
    ".txt": (FileType.DOC_MARKDOWN, "text"),
    # Configuration
    ".toml": (FileType.CONFIG, "toml"),
    ".yaml": (FileType.CONFIG, "yaml"),
    ".yml": (FileType.CONFIG, "yaml"),
    ".json": (FileType.CONFIG, "json"),
    ".jsonl": (FileType.CONFIG, "json"),
    ".cfg": (FileType.CONFIG, "ini"),
    ".ini": (FileType.CONFIG, "ini"),
    ".env": (FileType.CONFIG, "dotenv"),
    ".cmake": (FileType.CONFIG, "cmake"),
    ".jinja": (FileType.CONFIG, "jinja"),
    # Other (known language, no dedicated file type)
    ".pyx": (FileType.OTHER, "cython"),
    ".sh": (FileType.OTHER, "bash"),
    ".tpl": (FileType.OTHER, "template"),
    ".patch": (FileType.OTHER, "diff"),
    ".js": (FileType.OTHER, "javascript"),
    ".html": (FileType.OTHER, "html"),
    ".css": (FileType.OTHER, "css"),
}

# Exact file name (case-sensitive) -> (type, language)
SPECIAL_FILENAMES: dict[str, tuple[FileType, str]] = {
    "CMakeLists.txt": (FileType.CONFIG, "cmake"),
    "requirements.txt": (FileType.CONFIG, "requirements"),
    "MANIFEST.in": (FileType.CONFIG, "manifest"),
    ".clang-format": (FileType.CONFIG, "yaml"),
    ".shellcheckrc": (FileType.CONFIG, "ini"),
    "CODEOWNERS": (FileType.CONFIG, "codeowners"),
    "README": (FileType.DOC_MARKDOWN, "text"),
}

# File name prefix (case-sensitive) -> (type, language)
SPECIAL_PREFIXES: dict[str, tuple[FileType, str]] = {
    "Dockerfile": (FileType.CONFIG, "dockerfile"),
}

# Parent directory name -> (type, language) for everything inside it
SPECIAL_DIRS: dict[str, tuple[FileType, str]] = {
    "requirements": (FileType.CONFIG, "requirements"),
}
TEST_DIR_FILE = frozenset({
    "test",
    "tests",
    "conftest.py"
})


class CorpusLoader:
    def __init__(self, root: str, max_bytes: int = 500000) -> None:
        self.path_root = Path(root)
        self.max_bytes = max_bytes

    def load(self) -> tuple[list[SourceFile], list[ExcludedFile]]:
        if not self.path_root.exists():
            raise FileNotFoundError(
                "The path file do not exist maybe you need to unzip the file"
            )
        for path in (sorted(self.path_root.rglob("*"))):
            if path.is_file():
                relative_path = path.relative_to(self.path_root).as_posix()
                self._load_file(path, relative_path)

    def _load_file(self, path: Path, rel: str) -> SourceFile | str:
        is_exclude_step_one = self._path_exclusion(rel)
        if is_exclude_step_one:
            return is_exclude_step_one
        size_bytes = path.stat().st_size
        if size_bytes > self.max_bytes:
            return "too_large"
        raw = path.read_bytes()
        head = raw[:SNIFF_SIZE]
        if b"\x00" in head:
            return "binary"
        try:
            content = raw.decode(encoding="utf-8")
        except UnicodeDecodeError:
            return "encoding"
        if not content.strip():
            return "empty"
        filetype, language = self.classify(path=path)
        if (path.name == "__init__.py" and
           self._is_trivial_init(content=content)):
            return "trivial_init"
        segments = rel.split("/")
        return SourceFile(
            source=rel,
            type=filetype,
            language=language,
            top_dir=segments[0] if len(segments) > 1 else ".",
            is_test=self.is_test(rel=rel),
            size_bytes=size_bytes,
            n_lines=len(content.splitlines(keepends=True)),
            n_tokens=0,
            content=content
        )

    def _path_exclusion(self, rel: str) -> str | None:
        list_rel = rel.split("/")
        for s in list_rel:
            for reason, element_in in EXCLUDED.items():
                if s in element_in:
                    return reason
            if s.endswith(".egg-info"):
                return "build_artifact"
        return None

    @staticmethod
    def classify(path: Path) -> tuple[FileType, str]:
        extension = path.suffix.lower()
        special_dir = SPECIAL_DIRS.get(path.parent.name)
        if special_dir:
            return special_dir
        special = SPECIAL_FILENAMES.get(path.name)
        if special:
            return special
        special = SPECIAL_PREFIXES.get(path.stem)
        if special:
            return special
        normal = EXTENSIONS.get(extension)
        if normal:
            return normal
        if extension != "":
            return EXTENSIONS.get(extension, (FileType.OTHER,
                                              extension.split(".")[-1]))
        return EXTENSIONS.get(extension, (FileType.OTHER, "unknown"))

    @staticmethod
    def is_test(rel: str) -> bool:
        for s in [s for s in rel.split("/")]:
            if (
                s.startswith("test_") or
               s in TEST_DIR_FILE
               ):
                return True
        return False

    @staticmethod
    def _is_trivial_init(content: str) -> bool:
        try:
            tree = ast.parse(content)
            return all(CorpusLoader._is_decorative(node) for node in tree.body)
        except SyntaxError:
            return False

    @staticmethod
    def _is_decorative(node: ast.stmt) -> bool:
        if isinstance(node, ast.Pass):
            return True
        if (isinstance(node, ast.Expr) and
           isinstance(node.value, ast.Constant) and
           isinstance(node.value.value, (str, EllipsisType))):
            return True
        return False
