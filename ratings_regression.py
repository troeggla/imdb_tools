import sys

import matplotlib.pyplot as plt
import numpy as np
from get_series_rating import get_series_ratings
from sklearn.linear_model import LinearRegression


def get_model_for_season(data, season_nr):
    model = LinearRegression()
    X, Y = [], []

    for i, episode in enumerate(data):
        episode_season = int(episode[0].split(".")[0])

        if episode_season == season_nr:
            X.append(i)
            Y.append(episode[2])

    X = np.reshape(X, (-1, 1))
    Y = np.reshape(Y, (-1, 1))

    model.fit(X, Y)

    return X, Y, model


def main():
    if len(sys.argv) != 2:
        print "USAGE:", sys.argv[0], "[imdb_id]"
        sys.exit(1)

    ratings = list(get_series_ratings(sys.argv[1]))
    seasons = set([int(e[0].split(".")[0]) for e in ratings])

    for season in seasons:
        X, Y, model = get_model_for_season(ratings, season)

        plt.scatter(X, Y, color="black")
        plt.plot(X, model.predict(X))

    plt.xlim(-0.5, len(ratings))
    plt.show()


if __name__ == "__main__":
    main()
