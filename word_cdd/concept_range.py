from __future__ import annotations

from dataclasses import dataclass

from nltk.corpus.reader.wordnet import Synset

from .wordnet_graph import WordNetGraph


@dataclass(frozen=True)
class ConceptRange:
    lemma: str
    language: str
    synsets: tuple[Synset, ...]

    @property
    def size(self) -> int:
        return len(self.synsets)


class ConceptRangeFinder:
    """同一 lemma が連続して付与されている概念範囲を探索する。"""

    def __init__(self, graph: WordNetGraph) -> None:
        self.graph = graph

    @staticmethod
    def get_lemmas(
        synset: Synset,
        language: str,
    ) -> list[str]:
        return synset.lemma_names(language)

    def find_all(
        self,
        synset: Synset,
        language: str,
    ) -> dict[str, ConceptRange]:
        result: dict[str, ConceptRange] = {}

        for lemma in self.get_lemmas(synset, language):
            result[lemma] = self.find(
                lemma=lemma,
                start=synset,
                language=language,
            )

        return result

    def find(
        self,
        lemma: str,
        start: Synset,
        language: str,
    ) -> ConceptRange:
        found: set[Synset] = {start}
        visited: set[Synset] = set()
        stack = [start]

        while stack:
            current = stack.pop()

            if current in visited:
                continue

            visited.add(current)

            neighbors = self.graph.get_parents(current) + self.graph.get_children(current) + self.graph.get_siblings(current)

            for neighbor in neighbors:
                if neighbor in visited:
                    continue

                if lemma not in self.get_lemmas(
                    neighbor,
                    language,
                ):
                    continue

                found.add(neighbor)
                stack.append(neighbor)

        ordered = sorted(
            found,
            key=lambda synset: synset.name(),
        )

        return ConceptRange(
            lemma=lemma,
            language=language,
            synsets=tuple(ordered),
        )
