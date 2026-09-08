from __future__ import annotations

from dataclasses import dataclass

from nltk.corpus.reader.wordnet import Synset

from .concept_range import ConceptRange
from .wordnet_graph import WordNetGraph


@dataclass(frozen=True)
class ConceptComparison:
    first_lemma: str
    second_lemma: str

    first_synsets: tuple[Synset, ...]
    second_synsets: tuple[Synset, ...]

    common_synsets: tuple[Synset, ...]
    first_only_synsets: tuple[Synset, ...]
    second_only_synsets: tuple[Synset, ...]

    jaccard_similarity: float
    relation_type: str
    meaning_type: str | None


class ConceptClassifier:
    """2言語の概念範囲を比較し、重なりと階層差を分類する。"""

    def __init__(self, graph: WordNetGraph) -> None:
        self.graph = graph

    def compare(
        self,
        first: ConceptRange,
        second: ConceptRange,
    ) -> ConceptComparison:
        first_set = set(first.synsets)
        second_set = set(second.synsets)

        common = first_set & second_set
        first_only = first_set - second_set
        second_only = second_set - first_set
        union = first_set | second_set

        jaccard = len(common) / len(union) if union else 0.0

        relation_type = self._classify_relation(
            first_set=first_set,
            second_set=second_set,
        )

        meaning_type = self._classify_meaning_type(
            first_set=first_set,
            second_set=second_set,
        )

        return ConceptComparison(
            first_lemma=first.lemma,
            second_lemma=second.lemma,
            first_synsets=tuple(sorted(first_set, key=lambda x: x.name())),
            second_synsets=tuple(sorted(second_set, key=lambda x: x.name())),
            common_synsets=tuple(sorted(common, key=lambda x: x.name())),
            first_only_synsets=tuple(sorted(first_only, key=lambda x: x.name())),
            second_only_synsets=tuple(sorted(second_only, key=lambda x: x.name())),
            jaccard_similarity=jaccard,
            relation_type=relation_type,
            meaning_type=meaning_type,
        )

    @staticmethod
    def _classify_relation(
        first_set: set[Synset],
        second_set: set[Synset],
    ) -> str:
        if first_set == second_set:
            return "exact"

        if not first_set & second_set:
            return "disjoint"

        if first_set <= second_set or second_set <= first_set:
            return "inclusion"

        return "partial_overlap"

    def _classify_meaning_type(
        self,
        first_set: set[Synset],
        second_set: set[Synset],
    ) -> str | None:
        if first_set == second_set:
            return None

        first_layers = self._group_by_depth(first_set)
        second_layers = self._group_by_depth(second_set)

        first_layer_keys = set(first_layers.keys())
        second_layer_keys = set(second_layers.keys())

        common_layers = sorted(first_layer_keys & second_layer_keys)

        first_unique_layers = sorted(first_layer_keys - second_layer_keys)

        second_unique_layers = sorted(second_layer_keys - first_layer_keys)

        side_type = self._classify_side_difference(
            first_layers,
            second_layers,
            common_layers,
        )

        # 両方の言語にそれぞれ固有の階層が存在する
        if first_unique_layers and second_unique_layers:
            if side_type is None:
                return "B3"

            return f"B3 and {side_type}"

        # first側だけに固有階層が存在する
        if first_unique_layers:
            vertical_type = self._classify_vertical_difference(
                common_layers,
                first_unique_layers,
            )

            if side_type is None:
                return vertical_type

            if vertical_type is None:
                return side_type

            return f"{vertical_type} and {side_type}"

        # second側だけに固有階層が存在する
        if second_unique_layers:
            vertical_type = self._classify_vertical_difference(
                common_layers,
                second_unique_layers,
            )

            if side_type is None:
                return vertical_type

            if vertical_type is None:
                return side_type

            return f"{vertical_type} and {side_type}"

        # 階層の種類は同じだが、
        # 同一階層内のSynset構成が異なる
        return side_type

    def _group_by_depth(
        self,
        synsets: set[Synset],
    ) -> dict[int, set[Synset]]:
        result: dict[int, set[Synset]] = {}

        for synset in synsets:
            depth = self.graph.get_depth(synset)

            result.setdefault(
                depth,
                set(),
            ).add(synset)

        return result

    @staticmethod
    def _classify_side_difference(
        first_layers: dict[int, set[Synset]],
        second_layers: dict[int, set[Synset]],
        common_layers: list[int],
    ) -> str | None:
        for layer in common_layers:
            first = first_layers[layer]
            second = second_layers[layer]

            if first == second:
                continue

            if first - second and second - first:
                return "A1"

            return "A2"

        return None

    @staticmethod
    def _classify_vertical_difference(
        common_layers: list[int],
        unique_layers: list[int],
    ) -> str | None:
        if not common_layers or not unique_layers:
            return None

        upper = any(layer < min(common_layers) for layer in unique_layers)

        lower = any(layer > max(common_layers) for layer in unique_layers)

        if upper and lower:
            return "B4"

        if upper:
            return "B2"

        if lower:
            return "B1"

        return None
