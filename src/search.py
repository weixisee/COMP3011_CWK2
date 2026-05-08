from indexer import tokenise
import difflib

# function to get query suggestion
def get_suggestion(word: str, index: dict) -> str | None:

    """
    Provide suggestion of the closest mathcing word in the index. 

    Uses difflib.get_close_matches with a similariy cutoff of 0.6 to suggest
    corrections or misspelled query words. 

    Time complexity: O(N) where N represents the number of unique words in index

    Args:
        word: the misspelled or unrecognised word provide by user
        index: the dictionary that stores the inverted index to search for suggestions

    Returns:
        the closest matching word if similariy > 0.6, None otherwise
    """

    suggestions = difflib.get_close_matches(word, index.keys(), n=1, cutoff=0.6)
    return suggestions[0] if suggestions else None

def print_query(index:dict, query_word:str) -> None:

    """
        Print the inverted index for a particular word entered by the user

        It will return all the pages the word appears in along with its frequency, positions and TF-IDF score.
        
        Args:
            index: the dictionary that store the inverted index
            query_word: the word to look up in the index
    """
    query_word = query_word.lower()

    if query_word not in index:
        suggestion = get_suggestion(query_word, index)
        if suggestion:
            print(f"[ERROR]: Could not find '{query_word}' in index. Did you mean: '{suggestion}'?\n")
        else:
            print(f"{query_word}  not in index.\n")
        return 
    
    result = index[query_word]

    # sort and print the results based on tf-idf scores
    sorted_results = sorted(result.items(), key=lambda x: x[1]["tf_idf"], reverse=True)

    for url, data in sorted_results:
        print(f"URL: {url}")
        print(f"Frequency: {data['frequency']}")
        print(f"Positions: {data['positions']}")
        print(f"TF-IDF: {data['tf_idf']}")
        print()

# # find a given query phrase in the inverted index
def find_words(index:dict, query_words: list[str]) -> list[str]:

    """
    Find a given query phrase in the inverted index and returns a list of all pages that contain it, 
    ranked by the TF-IDF score. 

    It will return pages containing ALL query words sorted by TF-IDF relevance score (highest first).

    Time Complexity: O(W * D) where W represents the number of query words and D represents the number of documents per words
    Space Complexity O(D) for the results list

    Args:
        index: The dictionary that stores the inverted index
        query_words: List of query words to seaerch for 


    Returns:
        A list of URLs sorted by relevane with highest TF-IDF first. It will return an empty list if any of the query word
        is not found. 
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
    
    # conjunctive queries
    intersected_pages = set.intersection(* results_pages)

    def score(url):
        return sum(index[word][url]["tf_idf"] for word in words if url in index[word])
    
    # for conjuctive queries
    # return list(set.intersection(*results_pages))
    # return in highly relevance to lower relevance
    return sorted(intersected_pages, key=score, reverse=True)