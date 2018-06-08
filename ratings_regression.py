import sys

import matplotlib.pyplot as plt
import numpy as np
from get_series_rating import get_series_ratings
from itertools import chain
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score


def flatten(l):
    def f(acc, x):
        if isinstance(x, list):
            return acc + flatten(x)
        else:
            return acc + [x]

    return reduce(f, l, [])


def get_model(data):
    model = LinearRegression()
    X, Y = [], []

    if not (isinstance(data[0][0], int) or isinstance(data[0][1], tuple)):
        data = enumerate(data)

    for i, episode in data:
        X.append(i)
        Y.append(episode[3])

    X = np.reshape(X, (-1, 1))
    Y = np.reshape(Y, (-1, 1))

    model.fit(X, Y)

    return X, Y, model


def get_model_for_season(data, season_nr):
    def filter_season((_, episode)):
        episode_season = int(episode[0].split(".")[0])
        return episode_season == season_nr

    season_data = filter(filter_season, enumerate(data))
    return get_model(season_data)


def main():
    if len(sys.argv) != 2:
        print "USAGE:", sys.argv[0], "[imdb_id]"
        sys.exit(1)

    ratings = list(get_series_ratings(sys.argv[1]))
    seasons = set([int(e[0].split(".")[0]) for e in ratings if "." in e[0]])
    y_lower_lim = 10

    for season in seasons:
        X, Y, model = get_model_for_season(ratings, season)
        y_pred = model.predict(X)

        X = [n + 1 for n in X]

        lines = plt.plot(X, y_pred)
        plt.scatter(X, Y, color=lines[0]._color)

        y_lower_lim = min(flatten(Y) + [y_lower_lim])

        print season, "=>", r2_score(Y, y_pred)

    if len(seasons) > 1:
        X, Y, model = get_model(ratings)
        y_pred = model.predict(X)

        plt.plot(
            [n + 1 for n in X], y_pred,
            color="gray",
            linestyle="dashed",
            linewidth=0.5
        )

        print
        print "TOTAL:", r2_score(Y, y_pred)

    plt.xlim(0.5, len(ratings) + 0.5)
    plt.ylim(y_lower_lim - 0.5, 10.5)

    plt.title(ratings[0][1])
    plt.xlabel("Episode")
    plt.ylabel("Rating")

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
