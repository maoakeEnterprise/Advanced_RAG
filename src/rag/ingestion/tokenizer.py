from transformers import AutoTokenizer


class TokenCounter:
    def __init__(self, model_name: str, max_length: int | None = None) -> None:
        self.model_name = model_name
        self._tokenizer = AutoTokenizer.from_pretrained(model_name)
        self._max_length = max_length

    def count(self, text: str) -> int:
        out = self._tokenizer(text, add_special_tokens=False)
        return len(out["input_ids"])

    def count_batch(self, texts: list[str]) -> list[int]:
        batch = self._tokenizer(texts, add_special_tokens=False)["input_ids"]
        return [len(tmp) for tmp in batch]

    @property
    def max_length(self) -> int:
        if self._max_length is not None:
            return self._max_length
        declared = self._tokenizer.model_max_length
        if declared < 1000000:
            return declared
        raise ValueError(
            f"Unknown max length for {self.model_name}, pass max_length"
        )
