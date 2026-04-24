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

# ─────────────────────────────────────────────
# tokenise functions
# ─────────────────────────────────────────────

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

def test_tokenise_special_characters():
    tokens = tokenise("!!! ?< #?")
    assert tokens == []

def test_tokenise_single_characters():
    tokens = tokenise("a b c d")
    assert tokens == []

def test_tokenise_stopwords():
    tokens = tokenise("is are am")
    assert tokens == []

# ─────────────────────────────────────────────
# build index functions
# ─────────────────────────────────────────────


def test_build_index_single_page():
    pages = {
        "url1": "<html><body>life is beautiful life</body></html>"
    }

    index = build_index(pages)

    assert "life" in index
    assert "url1" in index["life"]
    assert index["life"]["url1"]["frequency"] == 2
    assert index["life"]["url1"]["positions"] == [0, 2]

def test_build_index_single_word():
    pages = {
        "url1": "<html><body>extraordinary</body></html>"
    }
    
    index =  build_index(pages)
    assert "extraordinary" in index
    assert index["extraordinary"]["url1"]["frequency"] == 1
    assert index["extraordinary"]["url1"]["positions"] == [0]

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

def test_build_index_empty_string_html():

    pages = {
        "url1": "<html><body>It is never too late to be what you might have been.</body></html>",
        "url2": ""
    }

    index = build_index(pages)
    assert "late" in index
    assert "url2" not in index.get("late", {})

def test_build_index_case_insensitive():
    pages = {
        "url1": "<html>hello Hello HELLO</html>"
    }

    index = build_index(pages)
    assert index["hello"]["url1"]["frequency"] == 3

def test_build_index_skips_page_with_no_tokens():
    pages = {
        "url1": "<html><body>is are the and</body></html>",  # all stopwords
        "url2": "<html><body>hello world</body></html>"
    }
    index = build_index(pages)
    assert "hello" in index
    assert "url1" not in index.get("hello", {})

# ─────────────────────────────────────────────
# TF-IDF ranking logic
# ─────────────────────────────────────────────

def test_build_index_contains_tfidf():
    pages = {
        "url1": "<html><body>life is beautiful</body></html>",
        "url2": "<html><body>life is good</body></html>"
    }

    index = build_index(pages)

    assert "tf_idf" in index["life"]["url1"]
    assert "tf_idf" in index["life"]["url2"]


def test_build_index_tfidf_is_float():
    pages = {
        "url1": "<html><body>life is beautiful</body></html>",
        "url2": "<html><body>life is good</body></html>"
    }

    index = build_index(pages)

    assert isinstance(index["life"]["url1"]["tf_idf"], float)


def test_build_index_tfidf_rare_word_scores_higher():
    pages = {
        "url1": "<html><body>life is beautiful unique</body></html>",
        "url2": "<html><body>life is good</body></html>"
    }

    index = build_index(pages)

    # "unique" only appears in url1, "life" appears in both
    # so "unique" should have higher TF-IDF than "life" in url1
    assert index["unique"]["url1"]["tf_idf"] > index["life"]["url1"]["tf_idf"]

# ─────────────────────────────────────────────
# Save and Load Index function
# ─────────────────────────────────────────────

def test_save_index_create_file(tmp_path):
    index = {"life": {"url1": {"frequency": 1, "positions": [0], "tf_idf": 0.5}}}
    path = tmp_path/"index.json"
    save_index(index, str(path))
    assert path.exists()

def test_save_index_invalid_path():
    index = {"life": {"url1": {"frequency": 1, "positions": [0], "tf_idf": 0.5}}}
    with pytest.raises(OSError):
        save_index(index, "/invalid/path/index.json")

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

def test_save_and_load_empty_index(tmp_path):
    index = {}

    path = tmp_path /"index.json"

    save_index(index, path)
    loaded = load_index(path)

    assert loaded == {}

def test_load_index_missing_file():
    
    with pytest.raises(FileNotFoundError):
        load_index("non_existent_index.json")

def test_load_index_return_type(tmp_path):
    index = {"life": {"url1": {"frequency": 1, "positions": [0], "tf_idf": 0.5}}}

    path = tmp_path/"index.json"

    save_index(index, path)
    loaded_index = load_index(path)
    assert isinstance(loaded_index, dict)

    



    

