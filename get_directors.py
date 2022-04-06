import requests
from bs4 import BeautifulSoup


def get_director(imdb_id):
    """Returns the director for the item with the given IMDB ID."""
    # Fetch page for with with the given IMDB ID
    data = requests.get("http://www.imdb.com/title/" + imdb_id, headers={
        "Accept-Language": "en"
    })

    # Parse page
    doc = BeautifulSoup(data.text, "html.parser")
    # Extract name of director from corresponding tag on page
    result = doc.find("span", itemprop="director").find("span").contents[0]

    return result


def get_directors_list():
    """Returns the list of directors for all films on IMDB's Top 250 as a generator."""
    # Fetch IMDB Top 250 page
    data = requests.get("http://www.imdb.com/chart/top", headers={
        "Accept-Language": "en"
    })
    # Parse page and extract table containing titles
    doc = BeautifulSoup(data.text, "html.parser")
    table = doc.find(class_="lister").find("tbody", class_="lister-list")

    # Iterate over all titles
    for cell in table.find_all("td", class_="titleColumn"):
        # Extract name of director from entry
        personnel = cell.a["title"]
        director = personnel.split(",")[0].replace(" (dir.)", "")

        # Yield director's name
        yield director.strip()


if __name__ == "__main__":
    # Print list of directors on IMDB's Top 250
    for director in get_directors_list():
        print(director)
