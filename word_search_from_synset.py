from all_synsets_get import All_Synstes_Get
# Wordnetをインポート
from nltk.corpus import wordnet as wn
import matplotlib.pyplot as plt
import networkx as nx
import openpyxl
import collections
from excel_module import excel_read_getter

class Word_Search_from_Synsets(All_Synstes_Get):
    def search(self):
        pass

def delete_word(word):
    word = word.replace('[', '')
    word = word.replace(']', '')
    return word

if __name__ == '__main__':
    #word_searcher = Word_Search_from_Synsets()
    #word_searcher.search_DFS(wn.synsets('entity')[0])
    result_list = excel_read_getter('../../../../ikkyu/Documents/研究/アンケートデータ/日中_単語アンケート_分析0521.xlsx', 'Sheet1',min_row=1)

    count_list = [] # 個数をカウントするリスト
    count_not_list = [] # 個数をカウントするリスト
    item_number = 1 # 問題のナンバー
    # ワードの中身を取り出す （1問ずつ）
    for item in result_list:
        print('{}, {} = {}, {}'.format(item[0], item[1], item[4], item[5]))
        flag = False
        word_list = []
        # ターゲットのsynsetを取得
        for i in range(2,4,1):
            words = item[i].split(', ')
            # ターゲットを検索するために整形し、word_listに入れておく
            for word in words:
                word = delete_word(word)
                if word not in word_list:
                    word_list.append(word)
        # word_listの中身からwnオブジェクトを取得
        for target in word_list:
            synsets = wn.synsets(target[8:target.find('.')])
            # 対象のsynsetかを確認
            for synset in synsets:
                if str(synset) == target:
                    lemmas_jpn = synset.lemma_names('jpn')
                    lemmas_cmn = synset.lemma_names('cmn')
                    lemmas_ind = synset.lemma_names('ind') # <-----インドネシア語
                    print(lemmas_jpn, lemmas_cmn)
                    #if lemmas_jpn == [] or lemmas_cmn == []:
                    if lemmas_cmn == [] or lemmas_jpn == []:
                        flag = True
            # 一つでも[]のリストがあったら、その問題ナンバーをリストに追加する
            if flag == True:
                count_list.append(item_number)
                break
        # 全てに単語が付随していた場合
        else:
            count_not_list.append(item_number)
        item_number += 1

    print(len(count_list))
    for number in count_not_list:
        print(number)
    print(count_not_list)