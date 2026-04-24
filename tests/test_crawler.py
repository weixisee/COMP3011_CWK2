import pytest
import requests
import sys
import os
from unittest.mock import Mock, patch
from bs4 import BeautifulSoup


sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
)

from crawler import fetch_page, parse_page, extract_links, crawl_site, BASE_URL

# ─────────────────────────────────────────────
# fetch page function
# ─────────────────────────────────────────────
def test_fetch_page_success():
    
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = "<html><body>Hello</body></html>"
    mock_response.raise_for_status = Mock()

    with patch("crawler.requests.get", return_value=mock_response):
        result = fetch_page("https://quotes.toscrape.com/")

    assert result == "<html><body>Hello</body></html>"


def test_fetch_page_404():
    mock_response = Mock()
    mock_response.raise_for_status.side_effect = requests.HTTPError()

    with patch("crawler.requests.get", return_value=mock_response):
        result = fetch_page("https://quotes.toscrape.com/badpage")

    assert result is None

def test_fetch_page_403():
    mock_response = Mock()
    mock_response.status_code = 403

    with patch("crawler.requests.get", return_value=mock_response):
        result = fetch_page("https://quotes.toscrape.com/")

    assert result is None


def test_fetch_page_timeout():
    with patch("crawler.requests.get", side_effect=requests.exceptions.Timeout):
        result = fetch_page("https://quotes.toscrape.com/")

    assert result is None


def test_fetch_page_connection_error():
    with patch("crawler.requests.get", side_effect=requests.exceptions.ConnectionError):
        result = fetch_page("https://quotes.toscrape.com/")

    assert result is None


def test_fetch_page_retries_on_failure():
    # First two attempts fail, third succeeds
    mock_success = Mock()
    mock_success.status_code = 200
    mock_success.text = "<html><body>Success</body></html>"

    with patch("crawler.requests.get", side_effect=[
        requests.exceptions.ConnectionError,
        requests.exceptions.ConnectionError,
        mock_success
    ]):
        with patch("crawler.time.sleep"):
            result = fetch_page("https://quotes.toscrape.com/")

    assert result == "<html><body>Success</body></html>"

def test_fetch_page_returns_none_after_all_retries_fail():
    with patch("crawler.requests.get", side_effect=requests.exceptions.ConnectionError):
        with patch("crawler.time.sleep"):
            result = fetch_page("https://quotes.toscrape.com/", retries=3)

    assert result is None

# ─────────────────────────────────────────────
# parse page function
# ─────────────────────────────────────────────
def test_parse_page_returns_beautifulsoup():
    result = parse_page("<html><body><p>Hello</p></body></html>")

    assert isinstance(result, BeautifulSoup)


def test_parse_page_reads_content_correctly():
    result = parse_page("<html><body><p>Hello</p></body></html>")

    assert result.find("p").text == "Hello"


def test_parse_page_handles_empty_string():
    result = parse_page("")

    assert isinstance(result, BeautifulSoup)


def test_parse_page_finds_links():
    result = parse_page('<html><body><a href="/page/2">Next</a></body></html>')

    assert result.find("a")["href"] == "/page/2"

# ─────────────────────────────────────────────
# extract link function
# ─────────────────────────────────────────────
def test_extract_links_absolute_internal():
    soup = BeautifulSoup(
        '<a href="https://quotes.toscrape.com/page/2">Next</a>',
        "html.parser"
    )
    links = extract_links(soup, BASE_URL)

    assert "https://quotes.toscrape.com/page/2" in links


def test_extract_links_resolves_relative():
    soup = BeautifulSoup(
        '<a href="/page/2">Next</a>',
        "html.parser"
    )
    links = extract_links(soup, BASE_URL)

    assert "https://quotes.toscrape.com/page/2" in links


def test_extract_links_ignores_external():
    soup = BeautifulSoup(
        '<a href="https://google.com">Google</a>',
        "html.parser"
    )
    links = extract_links(soup, BASE_URL)

    assert links == []


def test_extract_links_ignores_mailto():
    soup = BeautifulSoup(
        '<a href="mailto:test@test.com">Email</a>',
        "html.parser"
    )
    links = extract_links(soup, BASE_URL)

    assert links == []


def test_extract_links_returns_empty_when_no_links():
    soup = BeautifulSoup(
        "<p>No links here</p>",
        "html.parser"
    )
    links = extract_links(soup, BASE_URL)

    assert links == []


def test_extract_links_returns_multiple_links():
    soup = BeautifulSoup(
        """
        <a href="/page/2">Page 2</a>
        <a href="/page/3">Page 3</a>
        <a href="https://google.com">External</a>
        """,
        "html.parser"
    )
    links = extract_links(soup, BASE_URL)

    assert len(links) == 2

# ─────────────────────────────────────────────
# crawl page function
# ─────────────────────────────────────────────
def test_crawl_site_stores_fetched_page():
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = "<html><body><p>No links</p></body></html>"

    with patch("crawler.requests.get", return_value=mock_response):
        with patch("crawler.time.sleep"):
            pages = crawl_site(BASE_URL)

    assert BASE_URL in pages

# crawl site
def test_crawl_site_follows_internal_links():
    page1 = Mock()
    page1.status_code = 200
    page1.text = '<html><body><a href="/page/2">Next</a></body></html>'

    page2 = Mock()
    page2.status_code = 200
    page2.text = "<html><body><p>Last page</p></body></html>"

    with patch("crawler.requests.get", side_effect=[page1, page2]):
        with patch("crawler.time.sleep"):
            pages = crawl_site(BASE_URL)

    assert len(pages) == 2


def test_crawl_site_does_not_visit_same_url_twice():
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = f'<html><body><a href="{BASE_URL}">Home</a></body></html>'

    with patch("crawler.requests.get", return_value=mock_response) as mock_get:
        with patch("crawler.time.sleep"):
            crawl_site(BASE_URL)

    assert mock_get.call_count == 1


def test_crawl_site_skips_failed_pages():
    page1 = Mock()
    page1.status_code = 200
    page1.text = '<html><body><a href="/page/2">Next</a></body></html>'

    page2 = Mock()
    page2.status_code = 404

    with patch("crawler.requests.get", side_effect=[page1, page2]):
        with patch("crawler.time.sleep"):
            pages = crawl_site(BASE_URL)

    assert len(pages) == 1


def test_crawl_site_calls_sleep_with_politeness_window():
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = "<html><body></body></html>"

    with patch("crawler.requests.get", return_value=mock_response):
        with patch("crawler.time.sleep") as mock_sleep:
            crawl_site(BASE_URL)

    mock_sleep.assert_called_with(6)


def test_crawl_site_returns_dict():
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = "<html><body></body></html>"

    with patch("crawler.requests.get", return_value=mock_response):
        with patch("crawler.time.sleep"):
            pages = crawl_site(BASE_URL)

    assert isinstance(pages, dict)

def test_crawl_site_network_error():
    page1 = Mock()
    page1.status_code = 200
    page1.text = '<html><body><a href="/page/2">Next</a></body></html>'

    with patch("crawler.requests.get", side_effect=[
        page1,
        requests.exceptions.ConnectionError,
        requests.exceptions.ConnectionError,
        requests.exceptions.ConnectionError,
    ]):
        with patch("crawler.time.sleep"):
            pages = crawl_site(BASE_URL)
    
    assert len(pages) == 1
    assert BASE_URL in pages


def test_crawl_site_returns_empty_dict_on_immediate_failure():
    with patch("crawler.requests.get", side_effect=requests.exceptions.ConnectionError):
        with patch("crawler.time.sleep"):
            pages = crawl_site(BASE_URL)

    assert pages == {}