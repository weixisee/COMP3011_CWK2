from indexer import tokenise
import difflib

# function to get query suggestion
def get_suggestion(word: str, index: dict) -> str | None:

    suggestions = difflib.get_close_matches(word, index.keys(), n=1, cutoff=0.6)
    return suggestions[0] if suggestions else None

def print_query(index:dict, query_word:str) -> None:

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