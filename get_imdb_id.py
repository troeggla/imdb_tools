import sys
import requests
from bs4 import BeautifulSoup


def search_for_title(title, limit=10):
    """Yields tuples of IMDB IDs and titles corresponding to a search query."""

    # Replace spaces in query with plus symbols and lowercase the query
    query = "+".join(word.lower() for word in title.split(" "))
    # Build query url
    url = "http://www.imdb.com/find?s=tt&q=" + query

    # Fetch IMDB result page
    data = requests.get(url, headers={
        "Accept-Language": "en"
    })

    # Parse page and extract results
    doc = BeautifulSoup(data.text, "html.parser")
    results = doc.find_all("li", class_="find-result-item")

    # Iterate over results, yielding at most `limit` items
    for row in results[:limit]:
        title_link = row.find("a")

        # Get title
        title = title_link.text
        # Find corresponding IMDB ID
        imdb_id = title_link['href'].split("/")[2]

        # Yield results
        yield imdb_id, title


def main():
    """Called if script is called from the command line."""

    # Ensure a search term is passed through the command line
    if len(sys.argv) != 2:
        print("USAGE:", sys.argv[0], "[search_term]")
        sys.exit(1)

    # Perform IMDB search
    results = search_for_title(sys.argv[1])

    # Print results
    for imdb_id, title in results:
        print(imdb_id, "=>", title)


if __name__ == "__main__":
    main()
