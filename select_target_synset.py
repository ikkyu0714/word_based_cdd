"""
2023/12/05
抽出した単語ペアのデータのうち, 指定したsynsetにつながっているデータのみを選択する
"""

import openpyxl
from all_synsets_get_direct import All_Synsets_Get_Direct
from wordnet_search import Wordnet_Search
from nltk.corpus import wordnet as wn
from excel_module import excel_read_getter, excel_write
import networkx as nx

def synset_type_select(all_synset_netowork, target):
    select_list = []

    for data in data_list:
        synsets = data[2][1:-1].split(',')
        target_synset = all_synset_netowork.target_confirm(all_synset_netowork.trimword_search(synsets[0]), synsets[0])
        thing_path = nx.has_path(all_synset_netowork.G, wn.synsets('thing')[0], target=target_synset[0])
        physical_path = nx.has_path(all_synset_netowork.G, wn.synsets(target)[0], target=target_synset[0])
        if physical_path == True or thing_path == True:
            select_list.append(data)
    return select_list

if __name__ == '__main__':
    path = '../../../../ikkyu/Documents/研究/WordNet比較データ/単語ペア取得_1208_日本中国.xlsx'
    data_list = excel_read_getter(path, 'Sheet')

    all_synset_netowork = Wordnet_Search()
    all_synset_netowork.direct_graph_make_DFS(wn.synsets('entity')[0])

    #select_list = synset_type_select(all_synset_netowork, 'physical_entity')

    
    
    excel_write('../../../../ikkyu/Documents/研究/WordNet比較データ/(physical_entity_thing)リスト_1211_日中_単語補完なし.xlsx', select_list)