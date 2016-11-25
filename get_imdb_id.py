import sys
import requests
from bs4 import BeautifulSoup


def search_for_title(title, limit=10):
    query = "+".join(word.lower() for word in title.split(" "))
    url = "http://www.imdb.com/find?s=tt&q=" + query

    data = requests.get(url, headers={
        "Accept-Language": "en"
    })

    doc = BeautifulSoup(data.text, "html.parser")
    results = doc.find(class_="findList").find_all("tr", class_="findResult")

    for row in results[:limit]:
        title = row("td")[1].text.strip()
        imdb_id = row("td")[1].find("a")['href'].split("/")[2]

        yield imdb_id, title


def main():
    if len(sys.argv) != 2:
        print "USAGE:", sys.argv[0], "[search_term]"
        sys.exit(1)

    results = search_for_title(sys.argv[1])

    for imdb_id, title in results:
        print imdb_id, "=>", title


if __name__ == "__main__":
    main()
