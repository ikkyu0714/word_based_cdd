from __future__ import annotations

import csv
from pathlib import Path

from .concept_classifier import ConceptComparison


class CsvResultWriter:
    HEADER = [
        "source_synset",
        "first_language",
        "second_language",
        "first_lemma",
        "second_lemma",
        "first_range_size",
        "second_range_size",
        "common_size",
        "jaccard_similarity",
        "relation_type",
        "meaning_type",
        "first_synsets",
        "second_synsets",
        "common_synsets",
        "first_only_synsets",
        "second_only_synsets",
    ]

    def __init__(
        self,
        output_path: str | Path,
    ) -> None:
        self.output_path = Path(output_path)

    def write(
        self,
        source_synset: str,
        first_language: str,
        second_language: str,
        results: list[ConceptComparison],
    ) -> None:
        self.output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with self.output_path.open(
            "w",
            newline="",
            encoding="utf-8-sig",
        ) as f:
            writer = csv.DictWriter(
                f,
                fieldnames=self.HEADER,
            )

            writer.writeheader()

            for result in results:
                writer.writerow(
                    {
                        "source_synset": source_synset,
                        "first_language": first_language,
                        "second_language": second_language,
                        "first_lemma": result.first_lemma,
                        "second_lemma": result.second_lemma,
                        "first_range_size": len(result.first_synsets),
                        "second_range_size": len(result.second_synsets),
                        "common_size": len(result.common_synsets),
                        "jaccard_similarity": result.jaccard_similarity,
                        "relation_type": result.relation_type,
                        "meaning_type": result.meaning_type or "",
                        "first_synsets": self._serialize_synsets(result.first_synsets),
                        "second_synsets": self._serialize_synsets(result.second_synsets),
                        "common_synsets": self._serialize_synsets(result.common_synsets),
                        "first_only_synsets": self._serialize_synsets(result.first_only_synsets),
                        "second_only_synsets": self._serialize_synsets(result.second_only_synsets),
                    }
                )

    @staticmethod
    def _serialize_synsets(
        synsets,
    ) -> str:
        return ", ".join(synset.name() for synset in synsets)
