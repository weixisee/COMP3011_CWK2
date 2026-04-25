from indexer import tokenise
import difflib

# function to get query suggestion
def get_suggestion(word: str, index: dict) -> str | None:

    """
    Finds the closest matching word in the index using fuzzy matching.

    Uses difflib.get_close_matches with a similarity cutoff of 0.6
    to suggest corrections for misspelled query words.

    Time complexity: O(W) where W = number of unique words in index.

    Args:
        word: The misspelled or unrecognised query word.
        index: The inverted index to search for suggestions.

    Returns:
        The closest matching word if similarity > 0.6, None otherwise.
    """

    suggestions = difflib.get_close_matches(word, index.keys(), n=1, cutoff=0.6)
    return suggestions[0] if suggestions else None

def print_query(index:dict, query_word:str) -> None:

    """
    Prints the inverted index entry for a given word.

    Displays all pages the word appears in, along with frequency,
    positions and TF-IDF score. If the word is not found, suggests
    a similar word if one exists.

    Args:
        index: The inverted index dictionary.
        query_word: The word to look up in the index.
    """
    query_word = query_word.lower()

    query_word = query_word.lower()

    if query_word not in index:
        suggestion = get_suggestion(query_word, index)
        if suggestion:
            print(f"[ERROR]: Could not find '{query_word}' in index. Did you mean: '{suggestion}'?\n")
        else:
            print(f"{query_word}  not in index.\n")
        return 
    
    result = index[query_word]

    for url, data in result.items():
        print(f"URL: {url}")
        print(f"Frequency: {data['frequency']}")
        print(f"Positions: {data['positions']}")
        print()

# # find a given query phrase in the inverted index
def find_words(index:dict, query_words: list[str]) -> list[str]:

    """
    Finds pages containing all query words, ranked by TF-IDF score.

    Tokenises the query, removes stopwords and special characters,
    then returns pages containing ALL query words (conjunctive search),
    sorted by combined TF-IDF relevance score (highest first).

    If a query word is not found, suggests a similar word if one exists.

    Time complexity: O(Q * D) where Q = query words, D = documents per word.
    Space complexity: O(D) for the results list.

    Args:
        index: The inverted index dictionary.
        query_words: List of query words to search for.

    Returns:
        A list of URLs sorted by relevance (highest TF-IDF first).
        Returns empty list if any query word is not found.
    """

    if not query_words:
        return []

    # tokenise the query phrase
    words= tokenise(" ".join(query_words))

    # return empty list if there is no words left after removing stopwords, special characters
    if not words:
        return []

    results_pages = []

    for word in words:
        if word not in index:
            suggestion = get_suggestion(word,  index)
            if suggestion:
                print(f"[ERROR]: Could not find '{word}'. Did you mean: '{suggestion}'?\n")
            else:
                print(f"{word} not found in index")
            return []
        results_pages.append(set(index[word].keys()))
    
    # conjustive queries
    intersected_pages = set.intersection(* results_pages)

    def score(url):
        return sum(index[word][url]["tf_idf"] for word in words if url in index[word])
    
    # for conjuctive queries
    # return list(set.intersection(*results_pages))
    # return in highly relevance to lower relevance
    return sorted(intersected_pages, key=score, reverse=True)