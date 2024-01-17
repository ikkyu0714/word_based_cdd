"""
概念範囲が異なる単語ペアの概念のタイプを分別
"""
from wordnet_search import Wordnet_Search
from nltk.corpus import wordnet as wn
import networkx as nx
import excel_module
from collections import Counter

class Concept_range_type(Wordnet_Search):
    def concept_layer(self, synset_lists):
        #layer_count_dict = {}
        layer_list = []
        for synset in synset_lists:
            print(synset)
            synset = self.target_confirm(self.trimword_search(synset), synset)
            if synset == []:
                continue
            
            layer = nx.shortest_path_length(self.G, wn.synsets('entity')[0], target=synset[0])
            layer_list.append([synset, layer])
            #print(synset, 'の階層：', layer)
            """if layer in layer_count_dict:
                layer_count_dict[layer] += 1
            else:
                layer_count_dict[layer] = 1"""

        concept_layer_dict = {concept_layer_pair[1]: [] for concept_layer_pair in layer_list}
        for key in concept_layer_dict.keys():
            synset_list = []
            for concept_layer_pair in layer_list:
                if key == concept_layer_pair[1]:
                    synset_list.extend(concept_layer_pair[0])
            concept_layer_dict[key] = synset_list
        
        sorted_concept_layer_dict = {key: concept_layer_dict[key] for key in sorted(concept_layer_dict)}
        #print(sorted_concept_layer_dict)

        #print(layer_dict)
        #return layer_dict
        return sorted_concept_layer_dict
    
    def layer_conpare(self, layer_list1, layer_list2):
        # 階層の範囲が同じならTrue, 異なればFalse
        if set(layer_list1) == set(layer_list2):
            return True 
        else:
            return False
    
    def side_concept_diff(self, lang1_dict, lang2_dict, keys):
        for key in keys:
            # ある階層の概念のリストがことなるとき
            if lang1_dict[key] != lang2_dict[key]:
                # lang1のsynset集合からlist2のsynset集合の要素を引いて空ではない
                if list(set(lang1_dict[key])-set(lang2_dict[key])) != []:
                    # lang2のsynset集合からlist1のsynset集合の要素を引いて空ではない => 部分共通
                    if list(set(lang2_dict[key])-set(lang1_dict[key])) != []:
                        return 'A1'
                    # 包含
                    else:
                        return 'A2'
                # lang1のsynset集合からlist2のsynset集合の要素を引いて空のとき
                else:
                    # 包含
                    if list(set(lang2_dict[key])-set(lang1_dict[key])) != []:
                        return 'A2'
        return None

    def upper_or_lower_diff(self, common_layer, unique_keys):
        upper_flag = False
        lower_flag = False
        for key in unique_keys:
            # keyが共通の最小より小さい時 -> 上位の概念に差がある
            if key < min(common_layer):
                upper_flag = True
            # keyが共通の最大より大きい時 -> 下位の概念に差がある
            if key > max(common_layer):
                lower_flag = True
        
        if upper_flag and lower_flag:
            return "B4"
        elif upper_flag:
            return "B2"
        elif lower_flag:
            return "B1"
        else:
            return None

        

    def meaning_type(self, lang1_concept_layer_dict, lang2_concept_layer_dict):
        layer_judge = self.layer_conpare(list(lang1_concept_layer_dict.keys()), list(lang2_concept_layer_dict.keys()))
        # 階層が同じ場合
        if layer_judge == False:
            # 共通の階層を抜き出す
            common_layer = list(set(lang1_concept_layer_dict.keys()).intersection(set(lang2_concept_layer_dict.keys())))
            # 共通していないキーをさがす
            unique_key1_2 = list(set(lang1_concept_layer_dict.keys())-set(lang2_concept_layer_dict.keys()))
            unique_key2_1 = list(set(lang2_concept_layer_dict.keys())-set(lang1_concept_layer_dict.keys()))
            # お互いが異なるキーをもっている
            if unique_key1_2 != [] and unique_key2_1 != []:
                beside = self.side_concept_diff(lang1_concept_layer_dict, lang2_concept_layer_dict, common_layer)
                if beside == None:
                    return 'B3'
                else:
                    return ('B3 and {}').format(beside)
            elif unique_key1_2 != []:
                vertical = self.upper_or_lower_diff(common_layer, unique_key1_2)
                beside = self.side_concept_diff(lang1_concept_layer_dict, lang2_concept_layer_dict, common_layer)
                if beside == None:
                    return vertical
                else:
                    return ('{} and {}').format(vertical, beside)
            elif unique_key2_1 != []:
                vertical = self.upper_or_lower_diff(common_layer, unique_key2_1)
                beside = self.side_concept_diff(lang1_concept_layer_dict, lang2_concept_layer_dict, common_layer)
                if beside == None:
                    return vertical
                else:
                    return ('{} and {}').format(vertical, beside)

        else:
            beside = self.side_concept_diff(lang1_concept_layer_dict, lang2_concept_layer_dict, lang1_concept_layer_dict.keys())
            return beside

        
    def layer_type(self, layer_dict):
        if len(layer_dict) == 1:
            if list(layer_dict.values())[0] == 1:
                return '1-synset'
            else:
                return '兄弟'
        else:
            if all(value == 1 for value in layer_dict.values()):
                return '親子'
            else:
                middle_layer = False
                # 最上層と中間層と最下層が複数あるかどうかを判断
                for i in range(len(layer_dict)):
                    key = list(layer_dict.keys())[i]
                    if i == 0: # iが最初のとき
                        top_layer = layer_dict[key]
                    elif i == len(layer_dict) - 1: # iが最後の時
                        last_layer = layer_dict[key]
                    else: # iが真ん中の時
                        if layer_dict[key] > 1:
                            middle_layer = True
                
                # タイプを返す
                if top_layer == 1:
                    if middle_layer == False:
                        return 'そこ付き'
                    else:
                        if last_layer > 1:
                            return '台形'
                        else:
                            return '中膨れ'
                else:
                    if middle_layer == False:
                        if last_layer > 1:
                            return '砂時計'
                        else:
                            return '蓋付き'
                    else:
                        if last_layer > 1:
                            return '寸胴'
                        else:
                            return 'ホームベース'

def include_confirm(minority_list, major_list):
    for synset in minority_list:
        if synset not in major_list:
            return '部分共通'
    return '包含'

if __name__ == "__main__":
    word_range = Concept_range_type()
    word_range.direct_graph_make_DFS(wn.synsets('entity')[0])
    bfs_list = [wn.synsets('entity')[0]]

    concept_type = {}

    data = excel_module.excel_read_getter('../../../../ikkyu/Documents/研究/アンケートデータ/単語翻訳_(physical_entity_thing)リスト_0829.xlsx', "Sheet", min_row = 2)
    count = 1
    target_list = [30, 38, 52, 75, 98, 112, 112, 123, 142, 142, 151, 153, 168, 178, 187, 212, 213, 219, 227, 228, 241, 249, 249, 270, 302, 307, 313, 355, 382, 391, 416, 417, 427, 437, 492, 493, 501, 509, 512, 518, 520, 534, 548, 559, 635, 645, 662, 681, 689, 698, 717, 751, 789, 806, 815, 824, 830, 844, 848, 860, 860, 870, 885, 937, 943, 948, 982, 985, 992, 1035, 1038, 1039, 1042, 1060, 1060, 1097, 1119, 1121, 1125]
    target_dict = {}
    for line in data:
        jpn_synsets = word_range.pos_confirm(line[2].replace('[', '').replace(']', '').split(', '))
        zh_synsets = word_range.pos_confirm(line[3].replace('[', '').replace(']', '').split(', '))
        """if line[4] < line[5]:
            type_tag = include_confirm(jpn_synsets, zh_synsets)
        elif line[4] > line[5]:
            type_tag = include_confirm(zh_synsets, jpn_synsets)
        else:
            type_tag = '部分共通'"""

        jpn_layer_dict = word_range.concept_layer(jpn_synsets)
        zh_layer_dict = word_range.concept_layer(zh_synsets)
        type_tag = word_range.meaning_type(jpn_layer_dict, zh_layer_dict)

        if count in target_list:
            target_dict[count] = type_tag

        if type_tag in concept_type:
            concept_type[type_tag] += 1
        else:
            concept_type[type_tag] = 1
        count += 1
    
    count = 0
    for key in concept_type:
        print('key- {} : {}'.format(key, concept_type[key]))
        count += concept_type[key]
    print(count)
    print(Counter(target_dict.values()))
