from __future__ import annotations

import networkx as nx
from nltk.corpus import wordnet as wn
from nltk.corpus.reader.wordnet import Synset


class WordNetGraph:
    """WordNet の名詞階層を有向グラフとして扱うクラス。"""

    def __init__(self) -> None:
        self.graph = nx.DiGraph()

    def build(self, root: Synset | None = None) -> None:
        """root を起点に hyponym 方向へグラフを構築する。"""
        if root is None:
            root = wn.synset("entity.n.01")

        self.graph.clear()
        visited: set[Synset] = set()
        stack = [root]

        while stack:
            current = stack.pop()
            if current in visited:
                continue

            visited.add(current)
            self.graph.add_node(current)

            for child in current.hyponyms():
                self.graph.add_edge(current, child)
                if child not in visited:
                    stack.append(child)

    def get_parents(self, synset: Synset) -> list[Synset]:
        if synset not in self.graph:
            return []
        return list(self.graph.predecessors(synset))

    def get_children(self, synset: Synset) -> list[Synset]:
        if synset not in self.graph:
            return []
        return list(self.graph.successors(synset))

    def get_siblings(self, synset: Synset) -> list[Synset]:
        siblings: set[Synset] = set()

        for parent in self.get_parents(synset):
            siblings.update(self.get_children(parent))

        siblings.discard(synset)
        return list(siblings)

    def get_depth(self, synset: Synset, root: Synset | None = None) -> int:
        if root is None:
            root = wn.synset("entity.n.01")

        return nx.shortest_path_length(
            self.graph,
            root,
            synset,
        )
