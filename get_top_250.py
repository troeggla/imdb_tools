import requests
from bs4 import BeautifulSoup


def get_top_250():
    """Retrieves data for all entries on the IMDB Top 250."""

    # Fetch IMDB Top 250
    data = requests.get("http://www.imdb.com/chart/top", headers={
        "Accept-Language": "en"
    })
    # Parse page
    doc = BeautifulSoup(data.text, "html.parser")
    table = doc.find(class_="lister").find("tbody", class_="lister-list")

    # Iterate over entries in IMDB Top 250 list
    for row in table.find_all("tr"):
        title_col = row.find(class_="titleColumn")
        rating_col = row.find(class_="imdbRating")

        # Extract position, title, year and rating from entry
        position = int(title_col.contents[0].strip()[:-1])
        title = title_col.a.contents[0]
        year = int(title_col.span.contents[0].strip()[1:-1])
        rating = float(rating_col.strong.contents[0])

        # Yield result as a tuple
        yield position, title, year, rating


def main():
    """Called if script is called from the command line."""

    top250 = get_top_250()
    print("position,title,year,rating")

    # Print IMDB Top 250 as CSV
    for position, title, year, rating in top250:
        print(u'%d,"%s",%d,%.1f' % (position, title, year, rating))


if __name__ == "__main__":
    main()
