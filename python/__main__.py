import sys
from Recommender import Recommender

if __name__ == "__main__":
    _id = sys.argv[1]

    print("Thx :), Writing for {}".format(_id))

    recommender = Recommender(_id)
    recommender.init_setting()
    recommender.data_preprocessing()
    recommender.reco_kmeans()
    recommender.visual_filtering()
    recommender.save()
    recommender.end()
