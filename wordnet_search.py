from all_synsets_get_direct import All_Synsets_Get_Direct
# Wordnetをインポート
from nltk.corpus import wordnet as wn
import matplotlib.pyplot as plt
import networkx as nx
import openpyxl
import collections
from excel_module import excel_read_getter
import japanize_matplotlib
import pandas as pd
from scipy import stats

class Wordnet_Search(All_Synsets_Get_Direct):
    # synsetsリストからどれがもっとも上位か並べ替えを行う
    def pos_confirm(self, synset_list):
        length_dict = {} # 最上位概念までの最短経路を入れるリスト
        sorted_synset_list = []

        # list内のsynsetの最上位までの最短パス数を計測
        for synset in synset_list:
            # 文字からwordnetのsynsetを取得する
            node_list = wn.synsets(synset[8:synset.find('.')])
            for node in node_list:
                if str(node) == synset:
                    target_synset = node
            length_dict[synset] = nx.shortest_path_length(self.G, wn.synsets('entity')[0], target=target_synset)

        # パスの短い順に並べ替える
        for length_order in sorted(length_dict.values()):
            for key, value in length_dict.items():
                if value == length_order:
                    if key not in sorted_synset_list:
                        sorted_synset_list.append(key)

        return sorted_synset_list

    # str型のsynsetsリストから[]を削除する
    def delete_word_list(self, word_list):
        deleted_list = []
        for word in word_list:
            word = word.replace('[', '') 
            word = word.replace(']', '') # <-itemはsynsetを検索するワード
            deleted_list.append(word)
        return deleted_list

    # 共通のsynsetsを取得する
    def get_common(self, more_synsets, less_synsets):
        common_list = [] #共通のsynsetsを格納するリスト
        for more_synset in more_synsets:
            for less_synset in less_synsets:
                if more_synset == less_synset:
                    common_list.append(more_synset)
        return common_list

    # 根ノードまでのホップ数
    def rootnode_hops(self, nodes, item):
        # 検索結果のうち、対象の概念かを確認
        while nodes != []:
            # 検索結果のsynsetが対象のsynsetの場合
            if str(nodes[0]) == item:
                # hyponymようにsynsetsを作る
                hops_num = nx.shortest_path_length(self.G, wn.synsets('entity')[0], target=nodes[0])
                break
            else:
                nodes.pop(0)
        return hops_num

    # synsetsの文字列からwn.synsetを検索する
    def trimword_search(self, target):
        result = wn.synsets(target[8:target.find('.')])
        return result

    # 葉ノードまでのホップ数
    def leafnode_hops(self, nodes, target):
        hops_num = 0
        # 対象の概念かを確認する
        for node in nodes:
            if str(node) == target:
                #　 子ノードを格納
                hyponyms = self.get_children(node)
                leaf_node_list = [] # 葉ノードを入れるリスト
                # 幅優先探索で葉ノードを探索する
                while hyponyms != []:
                    pop = hyponyms.pop(0)
                    hypo_list = self.get_children(pop)
                    if hypo_list == []:
                        leaf_node_list.append(pop)
                    else:
                        hyponyms.extend(hypo_list)
                
                # 葉ノードの中から最長のホップ数を返す
                if leaf_node_list != []:
                    hops_list = [nx.shortest_path_length(self.G, node, leaf) for leaf in leaf_node_list] # ホップ数を格納するリスト
                    if max(hops_list) > hops_num:
                        hops_num = max(hops_list)

        return hops_num

    # ホップ数を取得する
    def get_hop(self, synsets, item):
        common_nodes = self.trimword_search(item) # 共通のsynsets
        top_nodes = self.trimword_search(synsets[0]) # 一番上のノード
        under_nodes = self.trimword_search(synsets[-1]) # 一番下のノード
        hype_hops = self.rootnode_hops(top_nodes, synsets[0]) 
        hypo_hops = self.leafnode_hops(under_nodes, synsets[-1])
        return hype_hops + hypo_hops + (len(synsets)-1)

    # 兄弟の数を取得するメソッド
    def get_bro(self, synsets, item):
        target_list = []
        for synset in synsets:
            # ターゲットとなるsynsetを取得する
            target_synset = self.target_confirm(self.trimword_search(synset), synset)
            target_list.extend(target_synset)

        #ターゲットから兄弟の数を取得する
        brother_list = [len(self.get_brothers(target)) for target in target_list]
        weight_list = [self.layer_get(target, nx.shortest_path(self.G, source=wn.synsets('entity')[0], target=target)) for target in target_list]
        return self.weighted_average(brother_list, weight_list)
        #return sum(brother_list)/len(brother_list) #平均
        #return sum(brother_list) # 総数

    def weighted_average(self, lists, weights):
        weighted_value = 0
        for item, weight in zip(lists, weights):
            weighted_value += item*weight
            #print('item:{}, weight:{} = {}'.format(item, weight, weighted_value)) #
        return weighted_value / sum(weights)

    def layer_get(self, target, paths):
        layer_weight = 1
        for path in reversed(paths):
            layer_weight *= 1/(len(self.get_brothers(path))+1)
        
        return layer_weight
            

    # ターゲットのsynsetか確認するメソッド
    def target_confirm(self, synsets, target):
        target_list = []
        # 検索で返されたsynsetの中からターゲットのsynsetを探す
        for synset in synsets: 
            if str(synset) == target:
                target_list.append(synset)

        return target_list

    def get_word_length(self, synsets, language):
        target_list = []
        word_count_list = []
        for synset in synsets:
            target_list.extend(self.target_confirm(self.trimword_search(synset), synset))
        
        for target in target_list:
            while target.lemma_names(language) == []:
                target = self.get_parent(target)[0]
            word_count_list.extend(target.lemma_names(language))
        #word_count_list = [len(target.lemma_names(language)) for target in target_list]
        word_count_list = list(set(word_count_list))
        print(word_count_list)
        #return sum(word_count_list)/len(word_count_list)
        #return sum(word_count_list)
        return len(word_count_list)

    # 各キーのバリューが何個ずつ存在するか確認する
    def count_num(self, count_list, t_list):
        counter_dict = collections.Counter(sorted(count_list))
        target_list = [count_list[index-1] for index in t_list]
        target_c = collections.Counter(target_list)

        return counter_dict, target_c

    # 各キーの個数をカウントするメソッド
    def hist_count_by_keys(self, count_dict, target_dict):
        height1 = []
        height2 = []
        sorted_keys = sorted(count_dict.keys())
        for key in sorted_keys:
            if key in target_dict.keys():
                height1.append(count_dict[key]-target_dict[key])
                height2.append(target_dict[key])
            else:
                height1.append(count_dict[key])
                height2.append(0)
        
        return height1, height2

    # 棒グラフを出力するメソッド
    def bar_graph(self, count_dict, target_dict, title):
        sorted_keys = sorted(count_dict.keys())
        height1, height2 = self.hist_count_by_keys(count_dict, target_dict)
        p1 = plt.bar(sorted_keys, height1, color='blue')
        p2 = plt.bar(sorted_keys, height2, bottom=height1, color='red')
        plt.legend((p1[0], p2[0]), ("有意差なし", "有意差あり"))
        plt.title(title)
        plt.xlabel('単語数')
        #plt.xlim(-5, 100)
        plt.savefig('../../../Downloads/'+title+'.png')
        #plt.show()

    def fisher_test(self, list1, list2, index_label, columns_label):
        #df = pd.DataFrame([list1, list2], index=index_label, columns=columns_label)
        df = pd.DataFrame([list1, list2])
        _, p = stats.fisher_exact(df)
        print(f'p値 = {p :.3f}')

    def chi2_test(self, list1, list2, index_label, columns_label):
        df = pd.DataFrame([list1, list2], index=index_label, columns=columns_label)
        print(df)

        chi2, p, dof, exp = stats.chi2_contingency(df, correction=False)
        #print("期待度数", "\n", exp)
        print("自由度", "\n", dof)
        print("カイ二乗値", "\n", chi2)
        print("p値", "\n", p)

    def print3D(self, X,Y,Z,color, alpha_params):
        #タイトルで漢字が使えるようフォントを設定
        #plt.rcParams['font.family'] = 'Meiryo'

        fig = plt.figure()
        ax = fig.add_subplot(projection='3d')
        ax.scatter(X, Y, Z, color=color, alpha=alpha_params)
        #グラフタイトルを設定
        ax.set_title("3D",size=20)
        #軸ラベルのサイズと色を設定
        ax.set_xlabel("Brother Num Average",size=15,color="black")
        ax.set_ylabel("Hop",size=15,color="black")
        ax.set_zlabel("Word Num Average",size=15,color="black")
        #plt.xlim(0,50)
        #plt.ylim(4,16)
        plt.show()

    def print2D(self, X, Y, color, alpha_params, x_label, y_label, xlim_list=None, ylim_list=None):
        plt.scatter(X, Y, s=50, color=color, alpha=alpha_params)
        plt.xlabel(x_label)
        plt.ylabel(y_label)
        if xlim_list is not None:
            plt.xlim(xlim_list[0],xlim_list[1])
        if ylim_list is not None:
            plt.ylim(ylim_list[0],ylim_list[1])
        plt.show()

if __name__ == '__main__':
    p_list = [10, 34, 46, 56, 57, 58, 94, 100, 120, 130, 131, 147, 148, 160, 170, 171, 175, 178, 179, 187]
    #p_list_2_1 = [46,58,100,131,148,175,187]
    #t_list = [3, 4, 5, 7, 8, 9, 12, 14, 15, 16, 17, 21, 28, 30, 37, 40, 44, 45, 46, 49, 50, 52, 53, 54, 55, 57, 58, 59, 60, 63, 65, 70, 71, 74, 75, 76, 78, 82, 87, 89, 90, 91, 93, 95, 97, 99, 107, 110, 116, 118, 120, 121, 122, 123, 124, 125, 126, 128, 129, 131, 132, 133, 134, 138, 141, 142, 143, 144, 147, 150, 152, 155, 157, 158, 160, 163, 164, 168, 169, 170, 172, 173, 174, 177, 178, 179, 180, 184, 185, 186, 187, 191, 192, 193, 194, 195]
    t_list = [i for i in range(1, 197) if i not in [2, 26, 43, 67]]

    wordnet_search = Wordnet_Search()
    wordnet_search.direct_graph_make_DFS(wn.synsets('entity')[0])

    # excel_read_getter関数でデータを読み取る
    result_list = excel_read_getter('../../../../ikkyu/Documents/研究/アンケートデータ/日中_単語アンケート_分析0521.xlsx', 'Sheet1', min_row=1)

    hop_count_list = [] # ホップ数をカウントしたものを入れるリスト
    bro_count_list = [] #
    word_count_list = [] #
    cmn_count_list = [] #
    jpn_count_list = [] #
    compare_list = [] #
    hop_per_list = []
    pos_list = []
    per_list = []
    else_count = 0 # elseに入った回数をカウント
    # 問題一行分
    for line in result_list:
        #if (line[4] == 1 and line[5] == 2) or (line[4] == 2 and line[5] == 1):
        if line[4] > line[5]: # 日本語より中国語の概念範囲が大きい場合
            compare_list.append('zh')
            more_synsets = line[2].split(', ') # 日本語が対応づいているsynsetをitemに格納
            less_synsets = line[3].split(', ')
        else: # 日本語の方が大きい場合
            if line[4] < line[5]:
                compare_list.append('jpn')
            else:
                compare_list.append('flat')
            more_synsets = line[3].split(', ') # 中国語が対応づいているsynsetをitemに格納
            less_synsets = line[2].split(', ')

        # "[" と "]"をitemから除去
        #print(more_synsets) #
        more_synsets = wordnet_search.delete_word_list(more_synsets)
        #print(more_synsets)
        less_synsets = wordnet_search.delete_word_list(less_synsets)

        more_synsets = wordnet_search.pos_confirm(more_synsets)
        less_synsets = wordnet_search.pos_confirm(less_synsets)
        item = wordnet_search.get_common(more_synsets, less_synsets)[0]

        # ホップ数をカウントする
        hop_count_list.append(wordnet_search.get_hop(more_synsets, item))

        # 兄弟数をカウントする
        bro_count_list.append(wordnet_search.get_bro(more_synsets, item))

        # 単語数をカウントする
        #word_count_list.append(get_word_length(more_synsets, 'cmn'))
        print('--------------------------------------')
        cmn_count_list.append(wordnet_search.get_word_length(more_synsets, 'cmn'))
        jpn_count_list.append(wordnet_search.get_word_length(more_synsets, 'jpn'))
        print('--------------------------------------')

    #word_dict, word_tar_c = count_num(word_count_list, p_list)
    #bar_graph(word_dict, word_tar_c, '多数派_(中国語)_平均')

    color_list = []
    for i in range(1, 197, 1):
        if compare_list[i-1] == 'zh':
            if i in p_list:
                color_list.append("red")
            else:
                color_list.append("mistyrose")
        elif compare_list[i-1] == 'jpn':
            if i in p_list:
                color_list.append("blue")
            else:
                color_list.append("lavender")
        else:
            if i in p_list:
                color_list.append("green")
            else:
                color_list.append("honeydew")
    
    cmn_target_list = [cmn_count_list[t-1] for t in t_list]
    jpn_target_list = [jpn_count_list[t-1] for t in t_list]
    hop_target_list = [hop_count_list[t-1] for t in t_list]
    bro_target_list = [bro_count_list[t-1] for t in t_list]
    color_target_list = [color_list[t-1] for t in t_list]

    #height1, height2 = hist_count_by_keys(word_dict, word_tar_c)
    #print(word_dict, word_tar_c)
    #chi2_test(height1, height2, ['有意差なし', '有意差あり'], sorted(word_dict.keys()))
    #fisher_test(height1, height2, ['有意差なし', '有意差あり'], sorted(word_dict.keys()))

    #print(sum(cmn_count_list)/len(cmn_count_list))
    #print(sum(jpn_count_list)/len(jpn_count_list))

    # 2Dの散布図を出力する時
    #wordnet_search.print2D(bro_target_list, hop_target_list, color_target_list, 0.5, '兄弟ノード数', 'ホップ数', [-1,50],  [-1,20]) # 
    # 3Dの散布図を出力する時
    #print3D(bro_count_list, hop_count_list, word_count_list, color_list, 0.5)

"""
from all_synsets_get import All_Synstes_Get
# Wordnetをインポート
from nltk.corpus import wordnet as wn
import matplotlib.pyplot as plt
import networkx as nx
import openpyxl
import collections
from excel_module import excel_read_getter
import japanize_matplotlib
import pandas as pd
from scipy import stats

class Wordnet_Search(All_Synstes_Get):
    # synsetsリストからどれがもっとも上位か並べ替えを行う
    def pos_confirm(self, synset_list):
        length_dict = {} # 最上位概念までの最短経路を入れるリスト
        sorted_synset_list = []

        # list内のsynsetの最上位までの最短パス数を計測
        for synset in synset_list:
            # 文字からwordnetのsynsetを取得する
            node_list = wn.synsets(synset[8:synset.find('.')])
            for node in node_list:
                if str(node) == synset:
                    target = node
            length_dict[synset] = nx.shortest_path_length(self.G, target, target=wn.synsets('entity')[0])

        # パスの短い順に並べ替える
        for length_order in sorted(length_dict.values()):
            for key, value in length_dict.items():
                if value == length_order:
                    if key not in sorted_synset_list:
                        sorted_synset_list.append(key)

        return sorted_synset_list

    # str型のsynsetsリストから[]を削除する
    def delete_word_list(self, word_list):
        deleted_list = []
        for word in word_list:
            word = word.replace('[', '') 
            word = word.replace(']', '') # <-itemはsynsetを検索するワード
            deleted_list.append(word)
        return deleted_list

    # 共通のsynsetsを取得する
    def get_common(self, more_synsets, less_synsets):
        common_list = [] #共通のsynsetsを格納するリスト
        for more_synset in more_synsets:
            for less_synset in less_synsets:
                if more_synset == less_synset:
                    common_list.append(more_synset)
        return common_list

    # 根ノードまでのホップ数
    def rootnode_hops(self, nodes, item):
        # 検索結果のうち、対象の概念かを確認
        while nodes != []:
            # 検索結果のsynsetが対象のsynsetの場合
            if str(nodes[0]) == item:
                # hyponymようにsynsetsを作る
                hops_num = nx.shortest_path_length(self.G, nodes[0], target=wn.synsets('entity')[0])
                break
            else:
                nodes.pop(0)
        return hops_num

    # synsetsの文字列からwn.synsetを検索する
    def trimword_search(self, target):
        result = wn.synsets(target[8:target.find('.')])
        return result

    # 葉ノードまでのホップ数
    def leafnode_hops(self, nodes, target):
        hops_num = 0
        # 対象の概念かを確認する
        for node in nodes:
            if str(node) == target:
                # 子ノードを格納
                hyponyms = self.get_hyponyms(node)
                leaf_node_list = [] # 葉ノードを入れるリスト
                # 幅優先探索で葉ノードを探索する
                while hyponyms != []:
                    pop = hyponyms.pop(0)
                    hypo_list = self.get_hyponyms(pop)
                    if hypo_list == []:
                        leaf_node_list.append(pop)
                    else:
                        hyponyms.extend(hypo_list)
                
                # 葉ノードの中から最長のホップ数を返す
                if leaf_node_list != []:
                    hops_list = [nx.shortest_path_length(self.G, leaf, node) for leaf in leaf_node_list] # ホップ数を格納するリスト
                    if max(hops_list) > hops_num:
                        hops_num = max(hops_list)

        return hops_num

    # ホップ数を取得する
    def get_hop(self, synsets, item):
        common_nodes = self.trimword_search(item) # 共通のsynsets
        top_nodes = self.trimword_search(synsets[0]) # 一番上のノード
        under_nodes = self.trimword_search(synsets[-1]) # 一番下のノード
        hype_hops = self.rootnode_hops(top_nodes, synsets[0]) 
        hypo_hops = self.leafnode_hops(under_nodes, synsets[-1])
        return hype_hops + hypo_hops + (len(synsets)-1)

    # 兄弟の数を取得するメソッド
    def get_bro(self, synsets, item):
        target_list = []
        for synset in synsets:
            # ターゲットとなるsynsetを取得する
            target_synset = self.target_confirm(self.trimword_search(synset), synset)
            target_list.extend(target_synset)

        #ターゲットから兄弟の数を取得する
        brother_list = [len(self.get_brothers(target)) for target in target_list]
        weight_list = [self.layer_get(target, nx.shortest_path(self.G, source=target, target=wn.synsets('entity')[0])) for target in target_list]
        return self.weighted_average(brother_list, weight_list)
        #return sum(brother_list)/len(brother_list) #平均
        #return sum(brother_list) # 総数

    def weighted_average(self, lists, weights):
        weighted_value = 0
        for item, weight in zip(lists, weights):
            weighted_value += item*weight
            #print('item:{}, weight:{} = {}'.format(item, weight, weighted_value)) #
        return weighted_value / sum(weights)

    def layer_get(self, target, paths):
        layer_weight = 1
        for path in reversed(paths):
            layer_weight *= 1/(len(self.get_brothers(path))+1)
        
        return layer_weight
            

    # ターゲットのsynsetか確認するメソッド
    def target_confirm(self, synsets, target):
        target_list = []
        # 検索で返されたsynsetの中からターゲットのsynsetを探す
        for synset in synsets: 
            if str(synset) == target:
                target_list.append(synset)

        return target_list

    def get_word_length(self, synsets, language):
        target_list = []
        word_count_list = []
        for synset in synsets:
            target_list.extend(self.target_confirm(self.trimword_search(synset), synset))
        
        for target in target_list:
            while target.lemma_names(language) == []:
                target = self.get_hypernyms(target)[0]
            word_count_list.extend(target.lemma_names(language))
        #word_count_list = [len(target.lemma_names(language)) for target in target_list]
        word_count_list = list(set(word_count_list))
        print(word_count_list)
        #return sum(word_count_list)/len(word_count_list)
        #return sum(word_count_list)
        return len(word_count_list)

    # 各キーのバリューが何個ずつ存在するか確認する
    def count_num(self, count_list, t_list):
        counter_dict = collections.Counter(sorted(count_list))
        target_list = [count_list[index-1] for index in t_list]
        target_c = collections.Counter(target_list)

        return counter_dict, target_c

    # 各キーの個数をカウントするメソッド
    def hist_count_by_keys(self, count_dict, target_dict):
        height1 = []
        height2 = []
        sorted_keys = sorted(count_dict.keys())
        for key in sorted_keys:
            if key in target_dict.keys():
                height1.append(count_dict[key]-target_dict[key])
                height2.append(target_dict[key])
            else:
                height1.append(count_dict[key])
                height2.append(0)
        
        return height1, height2

    # 棒グラフを出力するメソッド
    def bar_graph(self, count_dict, target_dict, title):
        sorted_keys = sorted(count_dict.keys())
        height1, height2 = self.hist_count_by_keys(count_dict, target_dict)
        p1 = plt.bar(sorted_keys, height1, color='blue')
        p2 = plt.bar(sorted_keys, height2, bottom=height1, color='red')
        plt.legend((p1[0], p2[0]), ("有意差なし", "有意差あり"))
        plt.title(title)
        plt.xlabel('単語数')
        #plt.xlim(-5, 100)
        plt.savefig('../../../Downloads/'+title+'.png')
        #plt.show()

    def fisher_test(self, list1, list2, index_label, columns_label):
        #df = pd.DataFrame([list1, list2], index=index_label, columns=columns_label)
        df = pd.DataFrame([list1, list2])
        _, p = stats.fisher_exact(df)
        print(f'p値 = {p :.3f}')

    def chi2_test(self, list1, list2, index_label, columns_label):
        df = pd.DataFrame([list1, list2], index=index_label, columns=columns_label)
        print(df)

        chi2, p, dof, exp = stats.chi2_contingency(df, correction=False)
        #print("期待度数", "\n", exp)
        print("自由度", "\n", dof)
        print("カイ二乗値", "\n", chi2)
        print("p値", "\n", p)

    def print3D(self, X,Y,Z,color, alpha_params):
        #タイトルで漢字が使えるようフォントを設定
        #plt.rcParams['font.family'] = 'Meiryo'

        fig = plt.figure()
        ax = fig.add_subplot(projection='3d')
        ax.scatter(X, Y, Z, color=color, alpha=alpha_params)
        #グラフタイトルを設定
        ax.set_title("3D",size=20)
        #軸ラベルのサイズと色を設定
        ax.set_xlabel("Brother Num Average",size=15,color="black")
        ax.set_ylabel("Hop",size=15,color="black")
        ax.set_zlabel("Word Num Average",size=15,color="black")
        #plt.xlim(0,50)
        #plt.ylim(4,16)
        plt.show()

    def print2D(self, X, Y, color, alpha_params, x_label, y_label, xlim_list=None, ylim_list=None):
        plt.scatter(X, Y, s=50, color=color, alpha=alpha_params)
        plt.xlabel(x_label)
        plt.ylabel(y_label)
        if xlim_list is not None:
            plt.xlim(xlim_list[0],xlim_list[1])
        if ylim_list is not None:
            plt.ylim(ylim_list[0],ylim_list[1])
        plt.show()

if __name__ == '__main__':
    p_list = [10, 34, 46, 56, 57, 58, 94, 100, 120, 130, 131, 147, 148, 160, 170, 171, 175, 178, 179, 187]
    #p_list_2_1 = [46,58,100,131,148,175,187]
    #t_list = [3, 4, 5, 7, 8, 9, 12, 14, 15, 16, 17, 21, 28, 30, 37, 40, 44, 45, 46, 49, 50, 52, 53, 54, 55, 57, 58, 59, 60, 63, 65, 70, 71, 74, 75, 76, 78, 82, 87, 89, 90, 91, 93, 95, 97, 99, 107, 110, 116, 118, 120, 121, 122, 123, 124, 125, 126, 128, 129, 131, 132, 133, 134, 138, 141, 142, 143, 144, 147, 150, 152, 155, 157, 158, 160, 163, 164, 168, 169, 170, 172, 173, 174, 177, 178, 179, 180, 184, 185, 186, 187, 191, 192, 193, 194, 195]
    t_list = [i for i in range(1, 197) if i not in [2, 26, 43, 67]]

    wordnet_search = Wordnet_Search()
    wordnet_search.search_DFS(wn.synsets('entity')[0])

    # excel_read_getter関数でデータを読み取る
    result_list = excel_read_getter('../../../../ikkyu/Documents/研究/アンケートデータ/日中_単語アンケート_分析0521.xlsx', 'Sheet1', min_row=1)

    hop_count_list = [] # ホップ数をカウントしたものを入れるリスト
    bro_count_list = [] #
    word_count_list = [] #
    cmn_count_list = [] #
    jpn_count_list = [] #
    compare_list = [] #
    hop_per_list = []
    pos_list = []
    per_list = []
    else_count = 0 # elseに入った回数をカウント
    # 問題一行分
    for line in result_list:
        #if (line[4] == 1 and line[5] == 2) or (line[4] == 2 and line[5] == 1):
        if line[4] > line[5]: # 日本語より中国語の概念範囲が大きい場合
            compare_list.append('zh')
            more_synsets = line[2].split(', ') # 日本語が対応づいているsynsetをitemに格納
            less_synsets = line[3].split(', ')
        else: # 日本語の方が大きい場合
            if line[4] < line[5]:
                compare_list.append('jpn')
            else:
                compare_list.append('flat')
            more_synsets = line[3].split(', ') # 中国語が対応づいているsynsetをitemに格納
            less_synsets = line[2].split(', ')

        # "[" と "]"をitemから除去
        #print(more_synsets) #
        more_synsets = wordnet_search.delete_word_list(more_synsets)
        #print(more_synsets)
        less_synsets = wordnet_search.delete_word_list(less_synsets)

        more_synsets = wordnet_search.pos_confirm(more_synsets)
        less_synsets = wordnet_search.pos_confirm(less_synsets)
        item = wordnet_search.get_common(more_synsets, less_synsets)[0]

        # ホップ数をカウントする
        hop_count_list.append(wordnet_search.get_hop(more_synsets, item))

        # 兄弟数をカウントする
        bro_count_list.append(wordnet_search.get_bro(more_synsets, item))

        # 単語数をカウントする
        #word_count_list.append(get_word_length(more_synsets, 'cmn'))
        print('--------------------------------------')
        cmn_count_list.append(wordnet_search.get_word_length(more_synsets, 'cmn'))
        jpn_count_list.append(wordnet_search.get_word_length(more_synsets, 'jpn'))
        print('--------------------------------------')

    #word_dict, word_tar_c = count_num(word_count_list, p_list)
    #bar_graph(word_dict, word_tar_c, '多数派_(中国語)_平均')

    color_list = []
    for i in range(1, 197, 1):
        if compare_list[i-1] == 'zh':
            if i in p_list:
                color_list.append("red")
            else:
                color_list.append("mistyrose")
        elif compare_list[i-1] == 'jpn':
            if i in p_list:
                color_list.append("blue")
            else:
                color_list.append("lavender")
        else:
            if i in p_list:
                color_list.append("green")
            else:
                color_list.append("honeydew")
    
    cmn_target_list = [cmn_count_list[t-1] for t in t_list]
    jpn_target_list = [jpn_count_list[t-1] for t in t_list]
    hop_target_list = [hop_count_list[t-1] for t in t_list]
    bro_target_list = [bro_count_list[t-1] for t in t_list]
    color_target_list = [color_list[t-1] for t in t_list]

    #for i in range(len(hop_count_list)):
        #if hop_count_list[i] < 7:
            #print(i+1, hop_count_list[i])

    #height1, height2 = hist_count_by_keys(word_dict, word_tar_c)
    #print(word_dict, word_tar_c)
    #chi2_test(height1, height2, ['有意差なし', '有意差あり'], sorted(word_dict.keys()))
    #fisher_test(height1, height2, ['有意差なし', '有意差あり'], sorted(word_dict.keys()))

    #print(sum(cmn_count_list)/len(cmn_count_list))
    #print(sum(jpn_count_list)/len(jpn_count_list))

    # 2Dの散布図を出力する時
    wordnet_search.print2D(bro_target_list, hop_target_list, color_target_list, 0.5, '兄弟ノード数', 'ホップ数', [-1,50],  [-1,20]) # 
    # 3Dの散布図を出力する時
    #print3D(bro_count_list, hop_count_list, word_count_list, color_list, 0.5)

"""