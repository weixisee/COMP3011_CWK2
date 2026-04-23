
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from collections import deque


# input URL
BASE_URL = "https://quotes.toscrape.com/"
POLITENESS_WINDOW = 6


def fetch_page(url:str, retries: int = 3) -> str | None:

    for attempt in range (1, retries + 1):
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                return response.text
            print(f"[WARNING] {url} returned HTTP {response.status_code}.\n")
            return None
        except requests.exceptions.RequestException as e:
            print(f"[WARNING] Attempt {attempt}/{retries} failed for {url} : {e}")
            if attempt < retries:
                time.sleep(2)

    print(f"[ERROR] All {retries} attempts failed to fetch {url}")
    return None

def parse_page(html:str) -> BeautifulSoup:

    return BeautifulSoup(html, 'html.parser')

def extract_links (soup: BeautifulSoup, current_url: str) -> list[str]:

    links = []

    for tag in soup.find_all("a", href=True):
        absolute = urljoin(current_url, tag["href"])
        parsed = urlparse(absolute)
        if parsed.netloc == urlparse(BASE_URL).netloc:
            links.append(absolute)
        
    return links
    

def crawl_site(start_url: str) -> dict[str, str]:

    # manage the url links, visited url links, and politeness request
    visited = set()
    queue = deque([start_url])
    visited.add(start_url)
    pages = {}

    while queue:
        
        url = queue.popleft()

        print(f"Fetching: {url}")
        html = fetch_page(url)

        if html is None:
            continue

        pages[url] = html
        soup = parse_page(html)
        links = extract_links(soup, url)

        for link in links:
            if link not in visited:
                visited.add(link)
                queue.append(link)

        print(f"[POLITENESS] Waiting {POLITENESS_WINDOW}s.\n")
        time.sleep(POLITENESS_WINDOW)

    print(f"[COMPLETED] Crawl complete. {len(pages)} pages fetched.\n")
    return pages

if __name__ == "__main__":
    crawl_site(BASE_URL)







