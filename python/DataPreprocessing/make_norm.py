import pandas as pd


def make_norm(features, reco_features=None):
    feature_cols = [features.columns[1:].values]

    if reco_features is None:
        norm_features = features.copy()
    else:
        norm_features = pd.concat(
            [features, reco_features], ignore_index=True).copy()
    for col in feature_cols:
        norm_features[col] = (norm_features[col] - norm_features[col].min()) / \
            (norm_features[col].max() - norm_features[col].min())

    return norm_features
