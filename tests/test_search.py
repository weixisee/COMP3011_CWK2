import pytest
import sys
import os

# Allow tests to import from src/
sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
)

from search import find_words, print_query

# define mock data for inverted index
@pytest.fixture
def sample_index():
    return {
        "life": {
            "url1": {"frequency": 2, "positions": [0, 3]},
            "url2": {"frequency": 1, "positions": [5]},
        },
        "beautiful": {
            "url1": {"frequency": 1, "positions": [2]},
        },
        "good": {
            "url2": {"frequency": 1, "positions": [1]},
        },
    }


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


def test_print_query_case_insensitive(sample_index, capsys):
    print_query(sample_index, "LiFe")

    captured = capsys.readouterr()
    output = captured.out

    assert "URL: url1" in output
    assert "URL: url2" in output


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

