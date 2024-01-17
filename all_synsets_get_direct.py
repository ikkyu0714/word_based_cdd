from nltk.corpus import wordnet as wn
import networkx as nx

class All_Synsets_Get_Direct():
    def __init__(self):
        self.G = nx.DiGraph()
        self.search_list = []

    # 深さ優先探索でwordnetからデータを取り出し, 有向グラフを作る
    def direct_graph_make_DFS(self, root):
        children = self.get_hyponyms(root)
        if children == []:
            return
        else:
            for child in children:
                self.G.add_edge(root, child)
                self.direct_graph_make_DFS(child)

    # wordnetからhyponymを取得
    def get_hyponyms(self, synset):
        hyponyms = synset.hyponyms()
        if hyponyms != []:
            return hyponyms
        else:
            return []
    
    # wordnetからhypernymを取得
    def get_hypernyms(self, synset):
        hypernyms = synset.hypernyms()
        if hypernyms != []:
            return hypernyms
        else:
            return []
        
    # グラフから親ノードをリスト型で返す
    def get_parent(self, node):
        return list(self.G.predecessors(node))
    
    # グラフから子ノードをリスト型で返す
    def get_children(self, node):
        return list(self.G.successors(node))
    
    def get_brothers(self, node):
        parent = self.get_parent(node)
        if parent == []: # 親がない場合
            return []
        else: # 親の子供を取り出し, その中から対象ノードを除いたノード(つまり兄弟ノードを返す)
            brothers = [child for child in self.get_children(parent[0]) if child != node]
            return brothers

if __name__ == '__main__':
    all_synsets_get = All_Synsets_Get_Direct()
    all_synsets_get.direct_graph_make_DFS(wn.synsets('entity')[0])
    print('ノード数:{}'.format(all_synsets_get.G.number_of_nodes()))
    print('エッジ数:{}'.format(all_synsets_get.G.number_of_edges()))
