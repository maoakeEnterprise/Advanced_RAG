from src.rag.ingestion.models import (SourceFile, ExcludedFile,
                                      FileType, ReasonType)


LINE = "=" * 60


def print_stats(source_files: list[SourceFile],
                excluded_files: list[ExcludedFile],
                top_n: int = 10) -> None:
    _print_by_type(source_files)
    _print_longest(source_files, top_n)
    _print_excluded(excluded_files)


def _print_by_type(source_files: list[SourceFile]) -> None:
    n_files = {t: 0 for t in FileType}
    n_tokens = {t: 0 for t in FileType}
    for file in source_files:
        n_files[file.type] += 1
        n_tokens[file.type] += file.n_tokens

    print(LINE)
    print("FICHIERS GARDÉS PAR TYPE")
    print(LINE)
    print(f"{'Type':<15}{'Fichiers':>10}{'Tokens':>14}{'Moyenne':>12}")
    for t in sorted(FileType, key=lambda t: n_tokens[t], reverse=True):
        mean = n_tokens[t] // n_files[t] if n_files[t] else 0
        print(f"{t:<15}{n_files[t]:>10}{n_tokens[t]:>14,}{mean:>12,}")
    total_files = len(source_files)
    total_tokens = sum(n_tokens.values())
    mean = total_tokens // total_files if total_files else 0
    print("-" * 51)
    print(f"{'TOTAL':<15}{total_files:>10}{total_tokens:>14,}{mean:>12,}\n")


def _print_longest(source_files: list[SourceFile], top_n: int) -> None:
    longest = sorted(source_files, key=lambda f: f.n_tokens,
                     reverse=True)[:top_n]
    print(LINE)
    print(f"TOP {top_n} DES FICHIERS LES PLUS LONGS (en tokens)")
    print(LINE)
    for i, file in enumerate(longest, start=1):
        print(f"{i:>2}. {file.n_tokens:>8,}  {file.type:<13} {file.source}")
    print()


def _print_excluded(excluded_files: list[ExcludedFile]) -> None:
    by_reason: dict[ReasonType, list[str]] = {r: [] for r in ReasonType}
    for file in excluded_files:
        by_reason[file.reason].append(file.source)

    print(LINE)
    print(f"FICHIERS EXCLUS ({len(excluded_files)})")
    print(LINE)
    print(f"{'Raison':<16}{'Fichiers':>9}  Exemple")
    for reason in sorted(ReasonType, key=lambda r: len(by_reason[r]),
                         reverse=True):
        sources = by_reason[reason]
        example = sources[0] if sources else "-"
        print(f"{reason:<16}{len(sources):>9}  {example}")
    print()
