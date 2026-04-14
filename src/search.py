from indexer import tokenise

def print_query(index:dict, query_word:str) -> None:

    query_word = query_word.lower()

    if query_word not in index:
        print(f"{query_word}  not in index.\n")
        return 
    
    result = index[query_word]

    for url, data in result.items():
        print(f"URL: {url} \n")
        print(f"Frequency: {data['frequency']}")
        print(f"Positions: {data['positions']}")

    print()


# # find a given query phrase in the inverted index
def find_words(index:dict, query_words: list[str]) -> list[str]:

    if not query_words:
        return []

    # tokenise the query phrase
    words= tokenise(" ".join(query_words))

    results_pages = []

    for word in words:
        if word not in index:
            return []
        results_pages.append(set(index[word].keys()))

    if len(results_pages) == 1:
        return list(results_pages[0])
    
    return list(set.intersection(*results_pages))
