from __future__ import annotations

import argparse
from pathlib import Path

import yaml
from nltk.corpus import wordnet as wn

from word_cdd.concept_classifier import ConceptClassifier
from word_cdd.concept_range import ConceptRangeFinder
from word_cdd.result_writer import CsvResultWriter
from word_cdd.wordnet_graph import WordNetGraph


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="WordNet 上の単語の概念範囲を2言語間で比較する")

    parser.add_argument(
        "--config",
        default="config/word_cdd.yaml",
        help="設定ファイルのパス",
    )

    return parser.parse_args()


def load_config(config_path: str | Path) -> dict:
    with Path(config_path).open(
        "r",
        encoding="utf-8",
    ) as f:
        return yaml.safe_load(f)


def main() -> None:
    args = parse_args()
    config = load_config(args.config)

    root_synset_name = config["wordnet"]["root_synset"]
    target_synset_name = config["wordnet"]["target_synset"]

    first_language = config["languages"]["first"]
    second_language = config["languages"]["second"]

    output_path = config["output"]["path"]

    if first_language == second_language:
        raise ValueError("first と second には異なる言語を指定してください")

    root_synset = wn.synset(root_synset_name)
    target_synset = wn.synset(target_synset_name)

    graph = WordNetGraph()
    graph.build(root_synset)

    range_finder = ConceptRangeFinder(graph)
    classifier = ConceptClassifier(graph)

    results = []
    seen_pairs: set[tuple[str, str]] = set()

    languages = [
        first_language,
        second_language,
    ]

    for language in languages:
        if language == first_language:
            other_language = second_language
        else:
            other_language = first_language

        source_ranges = range_finder.find_all(
            target_synset,
            language,
        )

        for source_range in source_ranges.values():
            for including_synset in source_range.synsets:
                compare_ranges = range_finder.find_all(
                    including_synset,
                    other_language,
                )

                for compare_range in compare_ranges.values():
                    if language == first_language:
                        first_range = source_range
                        second_range = compare_range
                    else:
                        first_range = compare_range
                        second_range = source_range

                    # 元コードと同じく、
                    # 概念範囲が同じペアは比較対象から除外
                    if set(first_range.synsets) == set(second_range.synsets):
                        continue

                    pair = (
                        first_range.lemma,
                        second_range.lemma,
                    )

                    if pair in seen_pairs:
                        continue

                    seen_pairs.add(pair)

                    comparison = classifier.compare(
                        first_range,
                        second_range,
                    )

                    results.append(comparison)

                    print(
                        f"{comparison.first_lemma} "
                        f"<-> {comparison.second_lemma} | "
                        f"{comparison.relation_type} | "
                        f"Jaccard="
                        f"{comparison.jaccard_similarity:.3f} | "
                        f"type={comparison.meaning_type}"
                    )

    writer = CsvResultWriter(output_path)

    writer.write(
        source_synset=target_synset.name(),
        first_language=first_language,
        second_language=second_language,
        results=results,
    )

    print(f"\nSaved: {output_path}")


if __name__ == "__main__":
    main()
