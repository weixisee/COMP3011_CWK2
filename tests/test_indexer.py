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

from indexer import extract_text, tokenise, build_index, save_index, load_index


def test_extract_text_removes_html_and_scripts():
    html = """
    <html>
        <head>
            <style>body {color:red;}</style>
            <script>alert("hi");</script>
        </head>
        <body>
            <p>Hello world</p>
        </body>
    </html>
    """

    text = extract_text(html)

    assert "Hello world" in text
    assert "alert" not in text
    assert "color:red" not in text


def test_tokenise_basic():
    text = "The Life is Beautiful!"

    tokens = tokenise(text)

    assert "life" in tokens
    assert "beautiful" in tokens
    assert "the" not in tokens
    assert "is" not in tokens


def test_tokenise_empty_string():
    tokens = tokenise("")
    assert tokens == []


def test_build_index_single_page():
    pages = {
        "url1": "<html><body>life is beautiful life</body></html>"
    }

    index = build_index(pages)

    assert "life" in index
    assert "url1" in index["life"]
    assert index["life"]["url1"]["frequency"] == 2
    assert index["life"]["url1"]["positions"] == [0, 2]


def test_build_index_multiple_pages():
    pages = {
        "url1": "<html>life is good</html>",
        "url2": "<html>life is beautiful</html>"
    }

    index = build_index(pages)

    assert "life" in index
    assert "url1" in index["life"]
    assert "url2" in index["life"]


def test_build_index_skips_empty_html():
    pages = {
        "url1": None,
        "url2": "<html>hello world</html>"
    }

    index = build_index(pages)

    assert "hello" in index
    assert "world" in index
    assert "url1" not in index.get("hello", {})


def test_save_and_load_index(tmp_path):
    index = {
        "life": {
            "url1": {
                "frequency": 1,
                "positions": [0]
            }
        }
    }

    path = tmp_path / "index.json"

    save_index(index, path)
    loaded = load_index(path)

    assert loaded == index


def test_load_index_missing_file():
    
    with pytest.raises(FileNotFoundError):
        load_index("non_existent_index.json")
    


