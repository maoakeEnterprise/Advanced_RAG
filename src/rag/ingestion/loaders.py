from pathlib import Path
from src.rag.ingestion.models import (SourceFile,
                                      ExcludedFile,
                                      FileType)

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
        pass

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
        special_dir = SPECIAL_DIRS.get(path.parent.name, None)
        if special_dir:
            return special_dir
        special = SPECIAL_FILENAMES.get(path.name, None)
        if special:
            return special
        special = SPECIAL_PREFIXES.get(path.name, None)
        if special:
            return special
        return EXTENSIONS.get(extension, "unknow")

    @staticmethod
    def is_test(rel: str) -> bool:
        for s in [s for s in rel.split("/")]:
            if s.startswith("test_") or s.endswith("_test"):
                return True
        return False

    @staticmethod
    def _is_trivial_init(content: str) -> bool:
        format_one = content.split("\n")
        tmp_list: list[str] = []
        for line in format_one:
            tmp_list.append(line.split["#"][0])
        tmp_txt = "\n".join(tmp_list)
        first_clear = tmp_txt.split["\"\"\""]
        tmp_list: list[str] = []
        for index, element in enumerate(first_clear):
            if index % 2 == 0:
                tmp_list.append(element)
        tmp_txt = "\n".join(tmp_list)
        return any(c.isalpha() for c in tmp_txt)
