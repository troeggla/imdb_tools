import sys
import requests
from bs4 import BeautifulSoup


def get_top_250():
    data = requests.get("http://www.imdb.com/chart/top", headers={
        "Accept-Language": "en"
    })
    doc = BeautifulSoup(data.text, "html.parser")
    table = doc.find(class_="lister").find("tbody", class_="lister-list")

    for row in table.find_all("tr"):
        title_col = row.find(class_="titleColumn")
        rating_col = row.find(class_="imdbRating")

        position = int(title_col.contents[0].strip()[:-1])
        title = title_col.a.contents[0]
        year = int(title_col.span.contents[0].strip()[1:-1])
        rating = float(rating_col.strong.contents[0])

        yield position, title, year, rating


def main():
    top250 = get_top_250()

    print("position,title,year,rating")

    for position, title, year, rating in top250:
        print(u'%d,"%s",%d,%.1f' % (position, title, year, rating))


if __name__ == "__main__":
    main()
