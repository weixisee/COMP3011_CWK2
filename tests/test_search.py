import pytest
import sys
import os

# Allow tests to import from src/
sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
)

from search import find_words, print_query
from indexer import build_index, save_index, load_index

# define mock data for inverted index
@pytest.fixture
def sample_index():
    return {
        "life": {
            "url1": {"frequency": 2, "positions": [0, 3], "tf_idf": 0.4},
            "url2": {"frequency": 1, "positions": [5], "tf_idf": 0.2},
        },
        "beautiful": {
            "url1": {"frequency": 1, "positions": [2], "tf_idf": 0.3},
        },
        "good": {
            "url2": {"frequency": 1, "positions": [1], "tf_idf": 0.3},
        },
    }


# ─────────────────────────────────────────────
# print query function
# ─────────────────────────────────────────────

def test_print_query_existing_word(sample_index, capsys):
    print_query(sample_index, "life")

    captured = capsys.readouterr()
    output = captured.out

    assert "URL: url1" in output
    assert "URL: url2" in output
    assert "Frequency:" in output
    assert "Positions:" in output


def test_print_query_word_not_found(sample_index, capsys):
    print_query(sample_index, "missing")

    captured = capsys.readouterr()
    output = captured.out.lower()

    assert "not in index" in output

def test_print_query_empty_string(sample_index, capsys):
    print_query(sample_index, "")

    captured = capsys.readouterr()
    output = captured.out.lower()

    assert "not in index" in output

def test_print_query_special_char(sample_index, capsys):
    print_query(sample_index, "??")

    captured = capsys.readouterr()
    output = captured.out.lower()

    assert "not in index" in output


def test_print_query_case_insensitive(sample_index, capsys):
    print_query(sample_index, "LiFe")

    captured = capsys.readouterr()
    output = captured.out

    assert "URL: url1" in output
    assert "URL: url2" in output

# ─────────────────────────────────────────────
# find words function
# ─────────────────────────────────────────────

def test_find_single_word(sample_index):
    result = find_words(sample_index, ["life"])
    assert set(result) == {"url1", "url2"}


def test_find_multiple_words(sample_index):
    result = find_words(sample_index, ["life", "beautiful"])
    assert result == ["url1"]


def test_find_word_not_in_index(sample_index):
    result = find_words(sample_index, ["nonexistent"])
    assert result == []


def test_find_empty_query(sample_index):
    result = find_words(sample_index, [])
    assert result == []


def test_find_case_insensitive(sample_index):
    result = find_words(sample_index, ["LiFe"])
    assert set(result) == {"url1", "url2"}

def test_find_stopword(sample_index):
    result = find_words(sample_index, ["and"])
    assert result == []

def test_find_single_char(sample_index):
    result = find_words(sample_index, ["a", "b", "c", "d"])
    assert result == []

def test_find_special_char(sample_index):
    result = find_words(sample_index, [">?"])
    assert result == []

def test_find_no_intersected_page(sample_index):
    result = find_words(sample_index, ["Beautiful", "Good"])
    assert result == []

# integration testing
def test_integration_build_load_print_find(tmp_path, capsys):

    # mock pages
    pages = {
        "url1":"<html><body>life is beautiful</body></html>",
        "url2": "<html><body>life is good</body></html>",
        "url3": "<html><body>something completely different</body></html>"
    }

    # build the index
    index = build_index(pages)

    # save the index as a json file
    path = tmp_path/"index.json"
    save_index(index, str(path))

    # load the index from index.json
    loaded_index = load_index(path)

    # print query - life
    print_query(loaded_index, "life")
    # catch the printed output from the terminal
    capture = capsys.readouterr()
    output = capture.out
    assert "url1" in output
    assert "url2" in output
    assert "Frequency" in output
    assert "Positions" in output
    assert loaded_index["life"]["url1"]["frequency"] >= 1
    assert len(loaded_index["life"]["url1"]["positions"]) >= 1
    assert "url3" not in loaded_index["life"]

    # find query
    # single word
    result = find_words(loaded_index, ["life"])
    assert set(result) == {"url1", "url2"}

    # multiple words - joint
    result = find_words(loaded_index, ["life", "good"])
    assert result == ["url2"]

