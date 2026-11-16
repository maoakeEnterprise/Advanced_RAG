from src.rag.ingestion.loaders import CorpusLoader
from src.rag.ingestion.models import (SourceFile, ExcludedFile,
                                      FileType, ReasonType)
from src.rag.ingestion.tokenizer import TokenCounter


EMBEDDING = "Qwen/Qwen3-Embedding-0.6B"


def print_loaded_file(files: tuple[list[SourceFile], list[ExcludedFile]]
                      ) -> None:
    typefile = {name: 0 for name in FileType}
    reason_file = {name: 0 for name in ReasonType}
    source, exclude = files
    for file in source:
        typefile[file.type] += 1
    for file2 in exclude:
        reason_file[file2.reason] += 1
    for file_t, number in typefile.items():
        print("=============================")
        print(f"FileType: {file_t}")
        print(f"Number: {number}")
    print("=============================\n")
    print("EXCLUDED FILE")
    for name, number in reason_file.items():
        print("=============================")
        print(f"Reason: {name}")
        print(f"Number: {number}")


if __name__ == "__main__":
    root = "data/raw/vllm-0.10.1"
    corpusLoader = CorpusLoader(root)
    tokenCounter = TokenCounter(model_name=EMBEDDING)
    source_files, excluded = corpusLoader.load()
    print_loaded_file(files=(source_files, excluded))
    contents = [sourcefile.content for sourcefile in source_files]
    batch_count = tokenCounter.count_batch(texts=contents)
    for sourcefile, n in zip(source_files, batch_count):
        sourcefile.n_tokens = n
