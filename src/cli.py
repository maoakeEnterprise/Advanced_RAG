from src.rag.ingestion.loaders import CorpusLoader
from src.rag.ingestion.stats import print_stats
from src.rag.ingestion.tokenizer import TokenCounter


class CLI:
    def __init__(self,
                 root: str = "data/raw/vllm-0.10.1",
                 embedding: str = "Qwen/Qwen3-Embedding-0.6B"
                 ) -> None:
        self.root = root
        self.embedding = embedding

    def ingest(self) -> None:
        self.tokenCounter = TokenCounter(model_name=self.embedding)
        corpusLoader = CorpusLoader(root=self.root)
        source_files, excluded = corpusLoader.load()
        contents = [sourcefile.content for sourcefile in source_files]
        batch_count = self.tokenCounter.count_batch(texts=contents)
        for sourcefile, n in zip(source_files, batch_count):
            sourcefile.n_tokens = n
        print_stats(source_files, excluded)

    def query(self, query: str, pipeline: str = "naive") -> None:
        pass

    def eval(self, pipeline: str = "naive") -> None:
        pass
