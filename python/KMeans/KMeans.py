import numpy as np
import math as mt
from sklearn.metrics.pairwise import euclidean_distances as euc
import random as ran
import pandas as pd


def tss(mean_pattern, df):
    A = np.expand_dims(mean_pattern.values, axis=0)
    tss = 0
    for idx in df.index:
        B = np.expand_dims(df.loc[idx].values, axis=0)
        tss += euc(
            B,
            A
        )[0][0] ** 2
    return tss


class KMeans:
    def __init__(self, datas):
        self.datas = datas.set_index("trackId")
        self.init_setting()

    def init_setting(self):
        datas_cnt = len(self.datas)

        self.K = round(mt.sqrt(datas_cnt / 2))

        mean_pattern = np.expand_dims(self.datas.mean().values, axis=0)
        norm_pattern = self.datas.values

        # TSS Logic
        self.tss = (euc(mean_pattern, norm_pattern) ** 2).sum()

    def run(self, early_stop_cnt=3, ecv_check_count=5):

        ecv_check = 0
        _round = 0
        _early_stop_cnt = 0
        _ecv_check_count = 0

        prev_clusters = None
        K_pattern = None
        datas = self.datas.copy()
        idxes = datas.index
        except_K = list()
        ecv_memories = np.array([])
        memories = list()

        while True:
            clusters = np.array([])
            # 초기 K 셋팅
            if _round == 0:
                init_K = np.array([])
                K_pattern = np.array([])
                datas_cnt = len(self.datas)

                while len(init_K) < self.K:
                    _K = ran.randrange(0, datas_cnt)
                    if _K in except_K:
                        continue

                    idx = idxes[int(_K)]
                    pattern = datas.loc[idx].values

                    if (_K not in init_K):
                        init_K = np.append(init_K, _K)
                        K_pattern = np.append(
                            K_pattern,
                            pattern
                        )
                r, c = datas.shape
                K_pattern = K_pattern.reshape(-1, c)

            for idx in datas.index:
                _pat = datas.loc[idx].values
                # euclidean distance based
                if _pat.ndim == 2:
                    _pat = _pat[0]
                _pat = np.expand_dims(_pat, axis=0)
                cluster = euc(_pat, K_pattern).argmin()
                clusters = np.append(clusters, cluster).astype("int")

                # improved similarity based
#                 cluster = np.array(
#                     [improved_similarity(_, _pat, w) for _ in K_pattern]
#                 ).argmax()
#                 clusters = np.append(clusters, cluster).astype("int")

            label_info = pd.DataFrame(clusters, columns=['label'])
            label_info.index = idxes

            wss = 0
            wss_list = np.array([])
            for label in range(0, self.K):
                cluster_in_idxes = label_info[
                    label_info['label'] == label
                ].index
                cluster_pat = np.expand_dims(
                    K_pattern[label],
                    axis=0
                )
                pattern = datas.loc[cluster_in_idxes].values

                _wss = (euc(pattern, cluster_pat) ** 2).sum()
                wss_list = np.append(wss_list, _wss / len(cluster_in_idxes))
                wss += _wss
            ecv = (1 - (wss / self.tss)) * 100

            if _early_stop_cnt != early_stop_cnt:
                if ecv < 80:
                    if ecv_check == ecv:
                        _early_stop_cnt += 1
                    ecv_check = ecv
                    _round += 1

                    # K 조정
                    for label in range(0, self.K):
                        cluster_in_idxes = label_info[
                            label_info['label'] == label
                        ].index
                        pattern = datas.loc[cluster_in_idxes].values.mean(
                            axis=0)
                        K_pattern[label] = pattern
                    continue
                else:
                    self.ecv = ecv
                    self.K_pattern = K_pattern
                    self.clusters = clusters
                    break
            else:
                if ecv < 80:
                    ecv_memories = np.append(ecv_memories, ecv)
                    memories.append((K_pattern, clusters))

                    # if _ecv_check_count == early_stop_cnt:
                    #     self.K_pattern = K_pattern
                    #     self.clusters = clusters
                    #     print("Clustering End.")
                    #     break
                    # else:
                    if _ecv_check_count == ecv_check_count:
                        max_idx = ecv_memories.argmax()
                        self.ecv = ecv_memories[max_idx]
                        memory = memories[max_idx]
                        self.K_pattern = memory[0]
                        self.clusters = memory[1]

                        break
                    else:
                        max_idx = wss_list.argmax()
                        except_K.append(int(init_K[max_idx]))

                        _round = 0
                        _early_stop_cnt = 0
                        _ecv_check_count += 1
                else:
                    self.K_pattern = K_pattern
                    self.clusters = clusters
                    break

    def sorting(self):
        k_pat = self.K_pattern
        _label = self.clusters

        eucs = list()
        sort_scores = list()
        for idx in range(0, len(k_pat)):
            sel_k_pat = np.expand_dims(k_pat[idx], axis=0)

            euc_scores = euc(sel_k_pat, k_pat)[0]
            sort_scores.append(euc_scores.argsort())
            eucs.append(euc_scores)

        # return np.array(eucs), np.array(sort_scores)
        # # print(eucs)

        # # print(sort_scores)
        sort_labels = list()
        while len(sort_labels) != len(k_pat):
            while True:
                sel_idx = ran.randrange(len(sort_scores))
                if sel_idx not in sort_labels:
                    break

            if (len(sort_labels) + 1) == len(self.K_pattern):
                sort_labels.append(sel_idx)

            check_sort = sort_scores[sel_idx][1:]
            for _s in check_sort:
                if _s not in sort_labels:
                    sort_labels.append(_s)
                    break

        change_index_info = list()
        for idx, _ in enumerate(sort_labels):
            change_index_info.append({
                "idxes": np.where(_label == _)[0],
                "change": idx
            })

        for info in change_index_info:
            _label[info['idxes']] = info['change']

        self.clusters = _label
        self.K_pattern = k_pat[sort_labels]

    def sorting_ver_2(self):
        k_pat = self.K_pattern
        _label = self.clusters

        eucs = list()
        sort_scores = list()
        for idx in range(0, len(k_pat)):
            sel_k_pat = np.expand_dims(k_pat[idx], axis=0)

            euc_scores = euc(sel_k_pat, k_pat)[0]
            sort_scores.append(euc_scores.argsort())
            eucs.append(euc_scores)

        eucs = np.array(eucs)
        sort_scores = np.array(sort_scores)

        # 초기 셋팅 (가장 전체적으로 유사도가 높은 친구, euc를기반으로 하니까 제일 낮은 친구가 선정되어야 함)
        sorting_labels = np.zeros(len(sort_scores)) - 1
        sort_eucs = np.array(eucs).sum(axis=0).argsort()

        top_eucs_cluster = sort_eucs[0]
        sorting_labels[0] = top_eucs_cluster

        # 초기 기반으로 가장 가까운 애들을 양쪽에 배치
        first_idx = 1
        last_idx = len(sort_scores) - 1

        sorting_labels[first_idx] = sort_scores[top_eucs_cluster][1]
        sorting_labels[last_idx] = sort_scores[top_eucs_cluster][2]

        first_cnt = 0
        last_cnt = 0

        while True:
            # traiding
            entry_1_idx = int(sorting_labels[first_idx + first_cnt])
            entry_2_idx = int(sorting_labels[last_idx - last_cnt])

            entry_1 = sort_scores[entry_1_idx]
            entry_2 = sort_scores[entry_2_idx]

            entry_1_euc = eucs[entry_1_idx]
            entry_2_euc = eucs[entry_2_idx]

            entry_1_sel = np.where(
                np.isin(entry_1, sorting_labels) == False)[0]
            entry_2_sel = np.where(
                np.isin(entry_2, sorting_labels) == False)[0]

            entry_1_cnt = 0
            entry_2_cnt = 0

            while True:
                _entry_1_sel = entry_1[entry_1_sel[entry_1_cnt]]
                _entry_2_sel = entry_2[entry_2_sel[entry_2_cnt]]

                if entry_1_euc[_entry_1_sel] > entry_2_euc[_entry_1_sel]:
                    _entry_1_sel = -1
                    entry_1_cnt += 1
                if entry_1_euc[_entry_2_sel] < entry_2_euc[_entry_2_sel]:
                    _entry_2_sel = -1
                    entry_2_cnt += 1

                if len(entry_1_sel) == (entry_1_cnt):
                    _entry_1_sel = "x"

                if len(entry_2_sel) == (entry_2_cnt):
                    _entry_2_sel = "x"

                if (_entry_1_sel != -1) & (_entry_2_sel != -1):
                    break

            if _entry_1_sel != "x":
                sorting_labels[first_idx + (first_cnt + 1)] = _entry_1_sel
                first_cnt += 1
            if _entry_2_sel != "x":
                sorting_labels[last_idx - (last_cnt + 1)] = _entry_2_sel
                last_cnt += 1

            if len(np.where(sorting_labels == -1)[0]) == 0:
                break

        change_index_info = list()
        for idx, _ in enumerate(sorting_labels):
            change_index_info.append({
                "idxes": np.where(_label == _)[0],
                "change": idx
            })

        for info in change_index_info:
            _label[info['idxes']] = info['change']

        self.clusters = _label
        self.K_pattern = k_pat[sorting_labels.astype("int")]
