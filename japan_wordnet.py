# Wordnetをインポート
from nltk.corpus import wordnet as wn

def word_similarity_jp(word1, word2):
    syn = []
    for i in range(len(wn.synsets(word1, lang="jpn"))):
        for j in range(len(wn.synsets(word2, lang="eng"))):
            syn.append(wn.synsets(word1, lang="jpn")[i].path_similarity(wn.synsets(word2, lang="eng")[j]))
    return syn
# 単語検索
#print(wn.synsets('earth'))

word1="change"
word2="cat" + '.n.01'

synsets = wn.synsets(word1)
all_synset = synsets[0].hyponyms()
for synset in all_synset:
    print(synset.hypernyms())
    for lemma in synset.lemmas():
        print(lemma.name())
"""print(wn.synsets(word1))
print(type(wn.synsets(word1)[0]))"""
#print(max(word_similarity_jp(word1, word2)))
