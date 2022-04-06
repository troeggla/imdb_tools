import sys
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime


def parse_episodes(doc):
    """Parse episodes from the season page of a series on IMDB"""
    # Find all TVEpisode items within the document
    eplist = doc.find("div", class_="eplist").find_all(
        itemtype="http://schema.org/TVEpisode"
    )

    # Iterate over all episodes
    for episode in eplist:
        # Get airdate for episode
        date_str = episode.find(class_="airdate").text.strip()

        try:
            # Parse airdate into datetime object
            airdate = datetime.strptime(
                date_str,
                "%d %b. %Y" if "May" not in date_str else "%d %b %Y"
            )

            # Ensure episode has already aired
            if datetime.now() > airdate:
                # Get title, episode number and episode info from entry
                title = episode.strong.text
                num = episode.find("meta", itemprop="episodeNumber")["content"]
                info = episode.find(class_="ipl-rating-star").find_all("span")

                # Get rating for episode if available
                if len(info) >= 2:
                    rating = float(info[1].text)
                else:
                    rating = 0.0

                # Get number of votes for episode if available
                if len(info) >= 3:
                    num_votes = int(re.sub(r"[^0-9]", "", info[2].text))
                else:
                    num_votes = 0

                # Yield extracted values
                yield num, title, rating, num_votes
        except ValueError:
            # Skip to next iteration if an exception occurs
            pass


def get_series_ratings(imdb_id):
    """Returns ratings for all episodes of the series with the given IMDB ID."""
    # Fetch list of episodes for given IMDB ID
    url = "http://www.imdb.com/title/" + imdb_id + "/episodes"
    data = requests.get(url, headers={
        "Accept-Language": "en"
    })

    # Parse document and find dropdown menu containing list of seasons
    doc = BeautifulSoup(data.text, "html.parser")
    seasons = doc.find("select", id="bySeason").find_all("option")

    # Parse episodes on initial page
    preselected_episodes = parse_episodes(doc)
    # Extract series title from initial page
    series_title = doc.find("h3", itemprop="name").a.text

    # Iterator over remaining seasons
    for season in seasons:
        # Yield seasons extracted from initial page
        if season.has_attr("selected"):
            for episode in preselected_episodes:
                # Prefix episode number with season number and yield
                episode_num = season["value"] + "." + episode[0]
                yield (episode_num, series_title) + episode[1:]
        else:
            # Fetch subsequent season page
            season_url = url + "?season=" + season["value"]
            data = requests.get(season_url, headers={
                "Accept-Language": "en"
            })

            # Parse season page
            doc = BeautifulSoup(data.text, "html.parser")
            # Parse episodes for season
            for episode in parse_episodes(doc):
                # Prefix episode number with season number and yield
                episode_num = season["value"] + "." + episode[0]
                yield (episode_num, series_title) + episode[1:]


def main():
    # Make sure an IMDB ID is passed through the command line
    if len(sys.argv) != 2:
        print("USAGE:", sys.argv[0], "[imdb_id]")
        sys.exit(1)

    # Get ratings for all episodes
    ratings = get_series_ratings(sys.argv[1])

    # Print episode ratings as CSV
    print("episode_num,name,title,rating,rating_count")
    for episode_info in ratings:
        print("\"%s\",\"%s\",\"%s\",%.1f,%d" % episode_info)


if __name__ == "__main__":
    main()
