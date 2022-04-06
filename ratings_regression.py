import sys

import matplotlib.pyplot as plt
import numpy as np
from get_series_rating import get_series_ratings
from functools import reduce
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score


def flatten(lst):
    """Flattens an arbitrarly nested list into a flat list."""
    def f(acc, x):
        # If param is a list, call flatten recursively, otherwise append item
        if isinstance(x, list):
            return acc + flatten(x)
        else:
            return acc + [x]

    # Flatten items in list by reducing over it with function f()
    return reduce(f, lst, [])


def get_model(data):
    """Generates a linear regression model given a set of episode ratings."""
    model = LinearRegression()
    X, Y = [], []

    # Generate indices for data if necessary
    if not (isinstance(data[0][0], int) or isinstance(data[0][1], tuple)):
        data = enumerate(data)

    # Populate X axis with episode numbers and Y axis with ratings
    for i, episode in data:
        X.append(i)
        Y.append(episode[3])

    # Transpose axes to work with model
    X = np.reshape(X, (-1, 1))
    Y = np.reshape(Y, (-1, 1))

    # Fit linear regression
    model.fit(X, Y)

    # Return axes with data and fitted model
    return X, Y, model


def get_model_for_season(data, season_nr):
    """Returns a linear regression model for a given season in a series dataset."""
    def filter_season(season):
        """Filtera the series by the given season"""
        _, episode = season

        # Extract season number
        episode_season = int(episode[0].split(".")[0])
        return episode_season == season_nr

    # Filter through series returning only desired seasons
    season_data = list(filter(filter_season, enumerate(data)))
    return get_model(season_data)


def parse_season_string(season_filter):
    """Parses a string into a list of seasons passed in from the command line."""
    filtered_seasons = []

    # Split string according to commas
    for expr in season_filter.split(","):
        # If expression contains hyphen, return a range of all numbers within
        # that range
        if "-" in expr:
            start, end = expr.split("-")
            filtered_seasons += range(int(start), int(end) + 1)
        else:
            # Otherwise, simple append expression
            filtered_seasons.append(int(expr))

    # Return list of seasons as numbers
    return filtered_seasons


def main():
    # Make sure an IMDB ID and optionally a list of seaons is passed in
    if len(sys.argv) < 2:
        print("USAGE:", sys.argv[0], "imdb_id [seasons]")
        sys.exit(1)

    # Get episode ratings for given IMDB ID
    ratings = list(get_series_ratings(sys.argv[1]))
    # Get available season numbers
    seasons = set([int(e[0].split(".")[0]) for e in ratings if "." in e[0]])
    # Lower limit for plot X-axis
    y_lower_lim = 10

    # Filter seasons by given string if available
    if len(sys.argv) >= 3:
        filtered_seasons = parse_season_string(sys.argv[2])
        seasons = [season for season in seasons if season in filtered_seasons]

    # Get regression model for each season
    for season in seasons:
        # Get model, X and Y data
        X, Y, model = get_model_for_season(ratings, season)
        # Predict regression line using X data
        y_pred = model.predict(X)

        # Make sure X values start from 1
        X = [n + 1 for n in X]

        # Plot regression line
        lines = plt.plot(X, y_pred)
        # Print scatter plot for episode ratings using same colour as regression
        plt.scatter(X, Y, color=lines[0]._color)

        # Ensure Y axis minimum is lowered if it is lower than `y_lower_lim`
        y_lower_lim = min(flatten(Y) + [y_lower_lim])

        # Print average script and R2 score for regression for season
        print(season, "=>", sum(Y) / len(Y), r2_score(Y, y_pred))

    # If series contains more than one season, generate regression for entire
    # series
    if len(seasons) > 1:
        # Get model for entire series and predict Y values given X data
        X, Y, model = get_model(ratings)
        y_pred = model.predict(X)

        # Plot overall regression as a dashed grey line
        plt.plot(
            [n + 1 for n in X], y_pred,
            color="gray",
            linestyle="dashed",
            linewidth=0.5
        )

        # Print R2 score for entire series
        print()
        print("TOTAL:", r2_score(Y, y_pred))

    # Set X and Y limits for plit
    plt.xlim(0.5, len(ratings) + 0.5)
    plt.ylim(-0.5, 10.5)

    # Add series title as plot title and label axes
    plt.title(ratings[0][1])
    plt.xlabel("Episode")
    plt.ylabel("Rating")

    # Show plot
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
