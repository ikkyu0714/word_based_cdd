# Wordnetをインポート
from nltk.corpus import wordnet as wn
# Networkxをインポート
import networkx as nx
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd

class All_Synstes_Get():
    def __init__(self):
        self.G = nx.Graph()
        self.search_list = []

    # 深さ優先探索
    def search_DFS(self, root):
        children = self.get_hyponyms(root)
        if children == []:
            return
        else:
            for child in children:
                self.G.add_edge(root, child)
                self.search_DFS(child)

    # matplotでグラフを描画 matplotは非推奨なので使わない方がいい
    def output_graph_matplot(self):
        pos = nx.spring_layout(self.G, seed=0)

        # グラフの描画
        plt.figure(figsize=(10,10)) #グラフエリアのサイズ
        nx.draw_networkx(self.G, pos) #グラフの描画(おまかせ)
        plt.show() #グラフの描画

    # 幅優先探索　これはリカーシブエラー出るからだめ
    def search_BFS(self, root):
        children = self.get_hyponyms(root)
        for child in children:
            self.G.add_edge(root, child)
            self.search_list.append(child)
        if self.search_list != []:
            self.search(self.search_list.pop(0))

    # 下位概念(子供)を取得
    def get_hyponyms(self, synset):
        if synset.hyponyms() != []:
            hyponyms = synset.hyponyms()
            return hyponyms
        else:
            return []

    # 兄弟を取得
    def get_brothers(self, synset):
        hypernyms = self.get_hypernyms(synset)
        if hypernyms != []:
            for hypernym in hypernyms:
                brothers = [brother for brother in self.get_hyponyms(hypernym) if brother != synset]
            return brothers
        else:
            return []

    # 上位概念(親)を取得
    def get_hypernyms(self, synset):
        if synset.hypernyms() != []:
            hypernyms = synset.hypernyms()
            return hypernyms
        else:
            return []

    def draw(self):
        nx.draw(self.G, with_labels=True)
        plt.show()

    def output_csv_data(self):
        # 空のDataFrameを用意する
        out = pd.DataFrame()
        for e in nx.cytoscape_data(self.G)["elements"]["edges"]:
            # "edges"の中に含まれるsource, target, weightの情報をDataFrameに追加する
            out = pd.concat(
                [
                    out,
                    pd.DataFrame(
                        {
                            "from": [e["data"]["source"]],
                            "to": [e["data"]["target"]],
                            #"weight": [e["data"]["weight"]],
                        }
                    )
                ]
            )
        out.reset_index(inplace=True, drop=True) # indexの振り直し
        out.to_csv("network.csv")

if __name__ == '__main__':
    all_synsets_get = All_Synstes_Get()
    all_synsets_get.search_DFS(wn.synsets('entity')[0])
    print('ノード数:{}'.format(all_synsets_get.G.number_of_nodes()))
    print('エッジ数:{}'.format(all_synsets_get.G.number_of_edges()))
    all_synsets_get.draw()
    #all_synsets_get.output_graph_matplot()
    #all_synsets_get.output_csv_data()
