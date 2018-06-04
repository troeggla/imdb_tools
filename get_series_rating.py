import sys
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime


def parse_episodes(doc):
    eplist = doc.find("div", class_="eplist").find_all(
        itemtype="http://schema.org/TVEpisode"
    )

    for episode in eplist:
        try:
            airdate = datetime.strptime(
                episode.find(class_="airdate").text.strip(),
                "%d %b. %Y"
            )

            title = episode.strong.text
            epnum = episode.find("meta", itemprop="episodeNumber")["content"]

            ratings = episode.find(class_="ipl-rating-star").find_all("span")
            rating = float(ratings[1].text)
            num_votes = int(re.sub(r"[^0-9]", "", ratings[2].text))

            yield epnum, title, rating, num_votes
        except ValueError:
            pass


def get_series_ratings(imdb_id):
    url = "http://www.imdb.com/title/" + imdb_id + "/episodes"
    data = requests.get(url, headers={
        "Accept-Language": "en"
    })

    doc = BeautifulSoup(data.text, "html.parser")
    seasons = doc.find("select", id="bySeason").find_all("option")

    preselected_episodes = parse_episodes(doc)

    for season in seasons:
        if season.has_attr("selected"):
            for episode in preselected_episodes:
                yield (season["value"] + "." + episode[0],) + episode[1:]
        else:
            season_url = url + "?season=" + season["value"]
            data = requests.get(season_url, headers={
                "Accept-Language": "en"
            })

            doc = BeautifulSoup(data.text, "html.parser")
            for episode in parse_episodes(doc):
                yield (season["value"] + "." + episode[0],) + episode[1:]


def main():
    if len(sys.argv) != 2:
        print "USAGE:", sys.argv[0], "[imdb_id]"
        sys.exit(1)

    ratings = get_series_ratings(sys.argv[1])

    print "episode_num,name,rating,rating_count"
    for episode_info in ratings:
        print "\"%s\",\"%s\",%.1f,%d" % episode_info


if __name__ == "__main__":
    main()
