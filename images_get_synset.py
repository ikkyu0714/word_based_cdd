from all_synsets_get_direct import All_Synsets_Get_Direct
# Wordnetをインポート
from nltk.corpus import wordnet as wn
import openpyxl
import random
from excel_module import excel_read_getter, excel_write
from wordnet_search import Wordnet_Search
import networkx as nx


class Wordnet_search_New(Wordnet_Search):
    def add_parent(self, synset_list):
        if len(synset_list) < 3:
            synset = synset_list[0]
            node_list = wn.synsets(synset[8:synset.find('.')])
            for node in node_list:
                if str(node) == synset:
                    parent = self.get_parent(node)[0]
            synset_list.insert(0, str(parent))
        
        return synset_list
    
    def choice_synset4questionnaire(self, synset_list, common_list):
        lst = []
        for str_synset in synset_list:
            length_dict = {}
            print(str_synset)
            # 文字からwordnetのsynsetを取得する
            synsets = wn.synsets(str_synset[8:str_synset.find('.')])
            for synset in synsets:
                if str(synset) == str_synset:
                    target = synset
            for common in common_list:
                for common_synset in wn.synsets(common[8:common.find('.')]):
                    if str(common_synset) == common:
                        if nx.has_path(self.G, source=common_synset, target=target):
                            length_dict[common] = nx.shortest_path_length(self.G, source=common_synset, target=target)
                        elif nx.has_path(self.G, source=target, target=common_synset):
                            length_dict[common] = nx.shortest_path_length(self.G, source=target, target=common_synset)
                        else:
                            pivot = target
                            while nx.has_path(self.G, source=pivot, target=common_synset) == False:
                                pivot = self.get_parent(pivot)[0]
                            length_dict[common] = nx.shortest_path_length(self.G, source=pivot, target=common_synset) + nx.shortest_path_length(self.G, source=pivot, target=target)
                            

            if any(value <= 2 for value in length_dict.values()):
                lst.append(str_synset)
        
        return lst

if __name__ == "__main__":
    all_synsets_get = Wordnet_search_New()
    all_synsets_get.direct_graph_make_DFS(wn.synsets('entity')[0])

    data = excel_read_getter('../../../../ikkyu/Documents/研究/アンケートデータ/日中尼_重複_1221_単語なし除外_日中尼単語確認.xlsx', 'Sheet', min_row=1)
    write_filename = '../../../../ikkyu/Documents/研究/アンケートデータ/日中尼_重複_0115_単語なし除外_日中尼単語確認_タスク選択.xlsx'
    excel_write_list = []

    for line in data:
        words = []
        # エクセルの3行目と4行目のsynsetを取り出す
        lists = line[3].split(', ')
        lists.extend(line[4].split(', '))
        lists.extend(line[5].split(', '))
        # []を取り除く
        trimwords = [word.replace('[', '').replace(']', '') for word in lists]
        # 重複を削除
        words = list(set(trimwords))
        # 重なっている部分を取得
        duplicates = list({x for x in trimwords if trimwords.count(x) > 1})
        # synsetのpositionを確認
        str_synsets_list = all_synsets_get.pos_confirm(words)
        pre_count = len(str_synsets_list)
        # アンケートに使うsynsetを絞る
        str_synsets_list = all_synsets_get.choice_synset4questionnaire(str_synsets_list, duplicates)
        print(pre_count, '--------->', len(str_synsets_list))
        # 親を追加
        #str_synsets_list = all_synsets_get.add_parent(str_synsets_list)

        while len(str_synsets_list) < 3:
            target = str_synsets_list[0]
            synset = all_synsets_get.target_confirm(all_synsets_get.trimword_search(target), target)
            str_synsets_list.insert(0, str(all_synsets_get.get_hypernyms(synset[0])[0]))
        
        synsets_list = [all_synsets_get.target_confirm(all_synsets_get.trimword_search(target), target)[0] for target in str_synsets_list]

        # 子供を格納する辞書 親がsynsets_list内にいる場合synset名, いない場合None
        children_dict = {}
        for synset in synsets_list:
            children_list = []
            flag = False
            for child in all_synsets_get.get_hyponyms(synset):
                if child in synsets_list:
                    children_list.append(child)
                    flag = True
            if flag == False:
                children_dict[synset] = None
            else:
                if children_list == []:
                    print(children_list)
                    exit()
                    #children_dict[synset] = None
                children_dict[synset] = children_list

        # 被らないようにキーワードを選ぶ (キーワードを全部使う)
        keywords_dict = {} 
        for synset in synsets_list:
            words = []
            for lemma in synset.lemma_names():
                if '_' in lemma:
                    lemma = lemma.replace('_', ' ')
                if ' ' in lemma:
                    lemma = '"' + lemma + '"'
                words.append(lemma)
            keywords_dict[synset] = ', '.join(words)
        
        keywords = []
        for key, value in keywords_dict.items():
            for synset, children in children_dict.items():
                if key == synset:
                    if children is None:
                        if ',' in value:
                            value = value.replace(',', '')
                        keywords.append(value)
                    else:
                        join_keyword = []
                        search_queue = children
                        #print(children_dict)
                        while search_queue != []:
                            pop = search_queue.pop()
                            for w in keywords_dict[pop].split(', '):
                                if '-' + w not in join_keyword:
                                    join_keyword.append('-' + w)
                            if children_dict[pop] is not None:
                                search_queue.extend(children_dict[pop])

                        #join_keyword = ['-' + keywords_dict[child] for child in children]
                        join_keyword = ' '.join(join_keyword)
                        keywords.append(value.replace(',', '') + ' ' + join_keyword)
        # 被らないようにキーワードを選ぶ (キーワードを一つ選ぶ)
        """for synset in synsets_list:
            for lemma in synset.lemma_names():
                if lemma not in keywords_dict.values():
                    if '_' in lemma:
                        lemma = lemma.replace('_', ' ')
                    if ' ' in lemma:
                        lemma = '"' + lemma + '"'
                    keywords_dict[synset] = lemma
                    break
            else:
                keywords_dict[synset] = lemma

        keywords = []
        for key, value in keywords_dict.items():
            for synset, children in children_dict.items():
                if key == synset:
                    if children is None:
                        keywords.append(value)
                    else:
                        join_keyword = []
                        search_queue = children
                        #print(children_dict)
                        while search_queue != []:
                            pop = search_queue.pop()
                            join_keyword.append('-' + keywords_dict[pop])
                            if children_dict[pop] is not None:
                                search_queue.extend(children_dict[pop])

                        #join_keyword = ['-' + keywords_dict[child] for child in children]
                        join_keyword = ' '.join(join_keyword)
                        keywords.append(value + ' ' + join_keyword)
                        #ここまで
                        join_keyword = ['-' + keywords_dict[child] for child in children]
                        if len(children) > 1:
                            join_keyword = ' AND '.join(join_keyword)
                            join_keyword = '(' + join_keyword + ')'
                        else:
                            join_keyword = join_keyword[0]
                        if type(join_keyword) == list:
                            print('ああああああああああああああ')
                            break
                        keywords.append(value + ' AND ' + join_keyword)"""
                        
        print(keywords)
        excel_write_list.append(keywords)

    excel_write(write_filename, excel_write_list)
