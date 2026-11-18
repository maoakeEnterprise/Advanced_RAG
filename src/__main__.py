from src.cli import CLI
import fire

EMBEDDING = "Qwen/Qwen3-Embedding-0.6B"
ROOT = "data/raw/vllm-0.10.1"


if __name__ == "__main__":
    fire.Fire(CLI)
