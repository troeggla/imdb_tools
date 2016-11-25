import sys
import requests
from bs4 import BeautifulSoup


def get_series_ratings(imdb_id):
    url = "http://www.imdb.com/title/" + imdb_id + "/epdate"
    data = requests.get(url, headers={
        "Accept-Language": "en"
    })

    doc = BeautifulSoup(data.text, "html.parser")
    table = doc.find(id="tn15content").find("table").find_all("tr")

    for row in table[1:]:
        cells = row.find_all("td")[:4]
        num, name, rating, count = [e.text.strip() for e in cells]

        yield num, name, float(rating), int(count.replace(",", ""))


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
