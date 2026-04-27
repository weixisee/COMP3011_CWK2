
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
    """
    Fetch and parse the robots.txt file of the targeted website

    Args:
        base_url (str): the base url of the website to crawl

    Returns:
        RobotFileParser: A RobotFileParser object that check URL permissions. 
        If there is no robots.txt file, it will return empty parser that allows 
        all the URLs.
    """

    rp = RobotFileParser()
    rp.set_url(urljoin(base_url, "/robots.txt"))
    try:
        rp.read()
        print(f"[CHECKING]: robots.txt loaded from {base_url}\n")
    except Exception as e:
        print(f"[ERROR] Could not load robots.txt: {e}.\n")
    return rp


def fetch_page(url:str, retries: int = 3) -> str | None:

    """
    Fetch the page of the given url with retry logic. There is up to 3 retry opportunities
    of a 2 seconds interval. 

    Args:
        url: the url of the page to fetch
        retries: Number of retry attempts on failure

    Returns:
        HTML content in string if successful, None otherwise
    """
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

    """
    Parse the raw HTML contents into a Beautiful Soap object

    Args:
        html: raw HTML contents in string data type 

    Returns:
        A BeautifulSoap object that represents the parsed HTML contents
    """

    return BeautifulSoup(html, 'html.parser')

def extract_links (soup: BeautifulSoup, current_url: str) -> list[str]:

    """
    Extract all the links exist in the parsed HTMl contents 

    Args: 
        soup: Parsed HTML content of the page
        current_url: the url of the current page that is being extracted for links

    Returns:
        A list of URLs found in the current page stored as string
    """

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

    """
    Crawl the website starting from the start_url using BFS

    Respects the robots.txt rule and the politeness window of 6s between each requests

    Time Complexity: O(N) where N represents the number of pages being crawled
    Space Complexity: O(N) for storing the visited URL and its raw HTML content

    Args:
        start_url: the URL the program starts crawling from

    Returns:
       A dictionary that maps each URL to its raw HTML content
    """

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

# if __name__ == "__main__":
#     crawl_site(BASE_URL)







