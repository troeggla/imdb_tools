import sys
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from threading import Thread


def parse_episodes(doc):
    """Parse episodes from the season page of a series on IMDB."""

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
    """Returns ratings for all episodes of the series with given IMDB ID."""

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

    # Shared data structure for storing retrieved data grouped by season
    season_data = {}

    def fetch_season_and_parse(season_number):
        """Fetches and parses the data associated to the given season."""
        # Fetch season page
        season_url = url + "?season=" + season_number
        data = requests.get(season_url, headers={
            "Accept-Language": "en"
        })

        # Initialise entry in shared data structure
        season_data[season_number] = []

        # Parse season page
        doc = BeautifulSoup(data.text, "html.parser")
        # Parse episodes for season
        for episode in parse_episodes(doc):
            episode_num = season_number + "." + episode[0]

            # Add parsed data to data strcture
            season_data[season_number].append(
                (episode_num, series_title) + episode[1:]
            )

    # List of threads
    threads = []

    # Iterate over remaining seasons
    for season in seasons:
        # Process season extracted from initial page
        if season.has_attr("selected"):
            season_data[season["value"]] = []

            for episode in preselected_episodes:
                # Prefix episode number with season number and yield
                episode_num = season["value"] + "." + episode[0]

                # Add data to data strcture
                season_data[season["value"]].append(
                    (episode_num, series_title) + episode[1:]
                )
        else:
            # Spawn new thread for fetching data for the given season
            thread = Thread(
                target=fetch_season_and_parse,
                args=(season["value"], )
            )

            # Append thread to list of threads and start it
            threads.append(thread)
            thread.start()

    # Wait for threads to complete
    for thread in threads:
        thread.join()

    # Sort retrieved data by season number
    for key in sorted(season_data):
        # Yield data for each episode separately
        for episode in season_data[key]:
            yield episode


def main():
    """Called if script is called from the command line."""

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
