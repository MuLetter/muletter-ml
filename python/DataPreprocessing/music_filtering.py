import pandas as pd
import numpy as np


def music_filtering(sel_tracks, kmeans):
    sel_tracks_ids = sel_tracks['trackId'].values

    label_info = pd.DataFrame(kmeans.clusters, columns=['label'])
    label_info.index = kmeans.datas.index
    _filtering_music = np.array([])

    for label in range(0, kmeans.K):
        cluster_in_idxes = label_info[
            label_info['label'] == label
        ].index

        # 사용자가 선택했던 음악이 군집에 속해있는지 확인
        for chk_id in cluster_in_idxes:
            if chk_id in sel_tracks_ids:
                _filtering_music = np.append(_filtering_music,
                                             cluster_in_idxes
                                             )
                break

    return _filtering_music
