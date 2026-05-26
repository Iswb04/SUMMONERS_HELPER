"""
import requests
from bs4 import BeautifulSoup # web scraping

WIKI_URL = "https://leagueoflegends.fandom.com/wiki/List_of_champions"

def def_release_dates(): # função pra buscar datas
    resp = requests.get(WIKI_URL)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    rows = soup.select("table.article-table tbody tr")
    release_dates = []

    for row in rows:
        cols = row.find_all("td")
        if len(cols) >= 4:
            date = cols[3].get_text(strip=True)
            release_dates.append(date)

    return release_dates


"""

