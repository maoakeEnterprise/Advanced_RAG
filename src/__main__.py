from src.rag.ingestion.loaders import CorpusLoader


if __name__ == "__main__":
    try:
        root = "data/raw/vllm-0.10.1"
        corpusLoader = CorpusLoader(root)
        corpusLoader.load()
        print("Hello World")
    except Exception as e:
        print(e)
