"""import openpyxl
from all_synsets_get_direct import All_Synsets_Get_Direct
from wordnet_search import Wordnet_Search
from nltk.corpus import wordnet as wn
from excel_module import excel_read_getter, excel_write
import networkx as nx

if __name__ == '__main__':
    path = '../../../../ikkyu/Documents/研究/アンケートデータ/単語翻訳_0720_1.xlsx'
    data_list = excel_read_getter(path, 'Sheet')

    all_synset_netowork = Wordnet_Search()
    all_synset_netowork.direct_graph_make_DFS(wn.synsets('entity')[0])

    select_list = []

    for data in data_list:
        synsets = data[2][1:-1].split(',')
        target_synset = all_synset_netowork.target_confirm(all_synset_netowork.trimword_search(synsets[0]), synsets[0])
        thing_path = nx.has_path(all_synset_netowork.G, wn.synsets('thing')[0], target=target_synset[0])
        physical_path = nx.has_path(all_synset_netowork.G, wn.synsets('physical_entity')[0], target=target_synset[0])
        if physical_path == True or thing_path == True:
            select_list.append(data)
    
    excel_write('../../../../ikkyu/Documents/研究/アンケートデータ/単語翻訳_(physical_entity_thing)リスト_0804.xlsx', select_list)
"""

import networkx as nx

# 有向グラフの作成
G = nx.DiGraph()

# グラフにノードとエッジを追加
G.add_nodes_from([1, 2, 3, 4, 5, 6])
G.add_edges_from([(1, 2), (1, 3), (2, 4), (3, 5), (5, 6)])

# 兄弟関係にあるノードを指定
node1 = 2
node2 = 6

pivot = node2
while nx.has_path(G, pivot, node1) == False:
    print(pivot)
    pivot = list(G.predecessors(pivot))[0]
print(nx.shortest_path_length(G, pivot, node1) + nx.shortest_path_length(G, pivot, node2))

