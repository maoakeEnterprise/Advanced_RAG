from pathlib import Path
from src.rag.ingestion.models import (SourceFile,
                                      ExcludedFile,
                                      FileType)


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

    def _path_exclusion(self, path: Path, rel: str) -> str | None:
        EXCLUDED_DIR = {
            ".git",
            "__pycache__",
            "node_modules",
            ".venv",
            "build",
            "dist",
            "*.egg-info",
            ".tox",
            ".mypy_cache"
            }
        VENDORED_DIR = {
            "third_party",
            "vendor",
            "vendored",
            "external",
            "extern",
            "3rdparty"
        }
        DATA_TEST_DIR = {
            "fixtures",
            "testdata",
            "test_data"
        }
        return None

    @staticmethod
    def classify(path: Path) -> tuple[FileType, str]:
        pass

    @staticmethod
    def is_test(rel: str) -> bool:
        pass

    @staticmethod
    def _is_trivial_init(content: str) -> bool:
        pass
