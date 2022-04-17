import matplotlib
import matplotlib.pyplot as plt
from sklearn.metrics.pairwise import euclidean_distances as euc
import datetime as dt


def visual_filtering(self):
    matplotlib.rc('font', family='AppleGothic')
    plt.rcParams['axes.unicode_minus'] = False
    plt.figure(figsize=(16, 4))

    _norm_features = self.norm_features.set_index("trackId").copy()
    _my_features = self.spotify.features.copy()
    _reco_features = self.spotify.reco_features.copy()

    feature_cols = _norm_features.columns.values

    my_norm_features = _norm_features.loc[_my_features['trackId']]
    r_norm_features = _norm_features.loc[_reco_features['trackId']]

    euc_check = euc(my_norm_features.values, r_norm_features.values).mean()
    # First Plot
    ax_1 = plt.subplot(1, 2, 1)
    ax_1.plot(feature_cols, r_norm_features.values.T, color='g', linewidth=0.1)
    ax_1.plot(feature_cols, my_norm_features.values.T, color='g', linewidth=2)
    ax_1.text(
        0.05,
        0.9,
        "평균거리 : {}".format(round(euc_check * 100) / 100),
        ha='left',
        transform=ax_1.transAxes
    )
    ax_1.set_title("필터링 전")

    # Second Plot
    r_norm_features_2 = _norm_features.loc[self.reco_musics['trackId']]
    euc_check = euc(my_norm_features.values, r_norm_features_2.values).mean()

    ax_2 = plt.subplot(1, 2, 2)
    ax_2.plot(feature_cols, r_norm_features_2.values.T,
              color='g', linewidth=0.1)
    ax_2.plot(feature_cols, my_norm_features.values.T, color='g', linewidth=2)
    ax_2.text(
        0.05,
        0.9,
        "평균거리 : {}".format(round(euc_check * 100) / 100),
        ha='left',
        transform=ax_2.transAxes
    )
    ax_2.set_title("필터링 후")

    now_time = dt.datetime.now().strftime("%Y%m%dT%H%M%Sms%f")
    self.visual_image = "./static/visual_{}.png".format(now_time)
    plt.savefig(self.visual_image.format(now_time))
