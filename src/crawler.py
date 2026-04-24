
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from collections import deque
from urllib.robotparser import RobotFileParser


# input URL
BASE_URL = "https://quotes.toscrape.com/"
POLITENESS_WINDOW = 6

def get_robot_parser(base_url: str) -> RobotFileParser:
    rp = RobotFileParser()
    rp.set_url(urljoin(base_url, "/robots.txt"))
    try:
        rp.read()
        print(f"[CHECKING]: robots.txt loaded from {base_url}\n")
    except Exception as e:
        print(f"[ERROR] Could not load robots.txt: {e}.\n")
    return rp


def fetch_page(url:str, retries: int = 3) -> str | None:

    for attempt in range (1, retries + 1):
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                return response.text
            elif response.status_code == 404:
                print(f"[WARNING] {url} not found (404).\n")
                return None
            elif response.status_code == 403:
                print(f"[WARNING] {url} access forbidden (403).\n")
                return None
            else:
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

        # if "/author/" in absolute or "/tag/" in absolute:
        #     continue

        if parsed.netloc == urlparse(BASE_URL).netloc:
            links.append(absolute)
        
    return links
    

def crawl_site(start_url: str) -> dict[str, str]:

    # manage the url links, visited url links, and politeness request
    visited = set()
    queue = deque([start_url])
    visited.add(start_url)
    pages = {}

    # check if there is a robot.txt file
    robot_file = get_robot_parser(start_url)

    while queue:
        
        url = queue.popleft()

        if not robot_file.can_fetch("*", url):
            print(f"[ROBOT] Skipping {url} becaused robots.txt does not allowed.\n")
            continue

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







