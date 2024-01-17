from nltk.corpus import wordnet as wn
import openpyxl
from excel_module import excel_read_getter, excel_write

def target_synset_search(str_target_synset):
    synsets = wn.synsets(str_target_synset[8:str_target_synset.find('.')])
    for synset in synsets:
        if str(synset) == str_target_synset:
            return synset
    else:
        print('===================', str_target_synset)
        
# synsetの単語群を返すメソッド
def word_get(synset, lang):
    return synset.lemma_names(lang)

def dict_insert(non_words_dict, key):
    if key in non_words_dict:
        non_words_dict[key] += 1
    else:
        non_words_dict[key] = 1
    return non_words_dict

path = '../../../Documents/研究/アンケートデータ/日中尼_重複_1215_2.xlsx'

data= excel_read_getter(path, "Sheet")

jpn_non_words_dict = {}
zh_non_words_dict = {}
non_words_dict = {}
target = ["Synset('o.k..n.01')", "Synset('st._andrew's_cross.n.01')", "Synset('st._augustine_grass.n.01')"]

synset_non_words_dict = {} # synsetに日本語か中国語がないかを記録する辞書
synset_count_dict = {} # synsetが何回でできたかを数える辞書

count = 0
non_count = 0
lst = []
for index, line in enumerate(data):
    count += 1
    flag = False
    jpn_synsets = line[3].replace('[', '').replace(']', '').split(', ')
    zh_synsets = line[4].replace('[', '').replace(']', '').split(', ')
    ind_synsets = line[5].replace('[', '').replace(']', '').split(', ')
    for synset in list(set(zh_synsets + jpn_synsets + ind_synsets)):
        # synsetをカウントする
        synset_count_dict = dict_insert(synset_count_dict, str(synset))
        if synset in target:
            continue
        jpn_words = word_get(target_synset_search(synset), 'jpn')
        zh_words = word_get(target_synset_search(synset), 'cmn')
        ind_words = word_get(target_synset_search(synset), 'ind')
        if jpn_words == [] or zh_words == [] or ind_words == []:
            flag = True
            non_words_dict = dict_insert(non_words_dict, index)
        synset_non_words_dict[str(synset)] = 'jpn and zh and ind' if (jpn_words == [] and zh_words == [] and ind_words) else 'jpn and zh' if (jpn_words == [] and zh_words == []) else 'zh and ind' if (zh_words == [] and ind_words == []) else 'jpn and ind' if (jpn_words == [] and ind_words == []) else 'jpn' if jpn_words == [] else 'zh' if zh_words == [] else 'ind' if ind_words == [] else 'None'
    if flag:
        non_count += 1
        lst.append(line)

    """for jpn_synset in jpn_synsets:
        if jpn_synset in target:
            continue
        #print(word_get(target_synset_search(jpn_synset), 'jpn'))
        if word_get(target_synset_search(jpn_synset), 'jpn') == [] or word_get(target_synset_search(jpn_synset), 'cmn') == []:
            non_words_dict = dict_insert(non_words_dict, index)
    for zh_synset in zh_synsets:
        if zh_synset in target:
            continue
        #print(word_get(target_synset_search(zh_synset), 'cmn'))
        if word_get(target_synset_search(zh_synset), 'cmn') == [] or word_get(target_synset_search(zh_synset), 'jpn') == []:
            non_words_dict = dict_insert(non_words_dict, index)"""
    
non_words_count = 0
for value in synset_non_words_dict.values():
    if value == 'jpn and zh and ind':
        non_words_count += 1

print('synset数：{}, 単語がないsynsetの個数：{}'.format(len(synset_count_dict), non_words_count))
print(count, non_count)

excel_write('../../../Documents/研究/アンケートデータ/日中尼_重複_1215_2_単語なし除外.xlsx', lst)