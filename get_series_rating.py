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
        date_str = episode.find(class_="airdate").text.strip()

        try:
            airdate = datetime.strptime(
                date_str,
                "%d %b. %Y" if "May" not in date_str else "%d %b %Y"
            )

            if datetime.now() > airdate:
                title = episode.strong.text
                num = episode.find("meta", itemprop="episodeNumber")["content"]
                info = episode.find(class_="ipl-rating-star").find_all("span")

                if len(info) >= 2:
                    rating = float(info[1].text)
                else:
                    rating = 0.0

                if len(info) >= 3:
                    num_votes = int(re.sub(r"[^0-9]", "", info[2].text))
                else:
                    num_votes = 0

                yield num, title, rating, num_votes
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
    series_title = doc.find("h3", itemprop="name").a.text

    for season in seasons:
        if season.has_attr("selected"):
            for episode in preselected_episodes:
                episode_num = season["value"] + "." + episode[0]
                yield (episode_num, series_title) + episode[1:]
        else:
            season_url = url + "?season=" + season["value"]
            data = requests.get(season_url, headers={
                "Accept-Language": "en"
            })

            doc = BeautifulSoup(data.text, "html.parser")
            for episode in parse_episodes(doc):
                episode_num = season["value"] + "." + episode[0]
                yield (episode_num, series_title) + episode[1:]


def main():
    if len(sys.argv) != 2:
        print("USAGE:", sys.argv[0], "[imdb_id]")
        sys.exit(1)

    ratings = get_series_ratings(sys.argv[1])

    print("episode_num,name,title,rating,rating_count")
    for episode_info in ratings:
        print("\"%s\",\"%s\",\"%s\",%.1f,%d" % episode_info)


if __name__ == "__main__":
    main()
