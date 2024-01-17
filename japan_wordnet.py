# Wordnetをインポート
from nltk.corpus import wordnet as wn

def word_similarity_jp(word1, word2):
    syn = []
    for i in range(len(wn.synsets(word1, lang="jpn"))):
        for j in range(len(wn.synsets(word2, lang="ind"))):
            syn.append(wn.synsets(word1, lang="jpn")[i].path_similarity(wn.synsets(word2, lang="ind")[j]))
    return syn
# 単語検索
#print(wn.synsets('earth'))

word1="craft"
word2="cat" + '.n.01'

synsets = wn.synsets(word1)
for synset in synsets:
    words = synset.lemma_names('cmn')
    print(synset)
    print(words)
#print(max(word_similarity_jp(word1, word2)))
