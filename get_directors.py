import requests
import sys
from bs4 import BeautifulSoup

from get_imdb_id import search_for_title


def get_director(imdb_id):
    data = requests.get("http://www.imdb.com/title/" + imdb_id, headers={
        "Accept-Language": "en"
    })

    doc = BeautifulSoup(data.text, "html.parser")
    result = doc.find("span", itemprop="director").find("span").contents[0]

    return result


def get_directors_list():
    data = requests.get("http://www.imdb.com/chart/top", headers={
        "Accept-Language": "en"
    })
    doc = BeautifulSoup(data.text, "html.parser")
    table = doc.find(class_="lister").find("tbody", class_="lister-list")

    for cell in table.find_all("td", class_="titleColumn"):
        personnel = cell.a["title"]
        director = personnel.split(",")[0].replace(" (dir.)", "")
        cast = personnel.split(",")[1:]

        yield director.strip()
        # for actor in cast:
        #     yield actor.strip()


if __name__ == "__main__":
    for director in get_directors_list():
        print(director)
