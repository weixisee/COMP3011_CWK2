import re
import json
from bs4 import BeautifulSoup
import math


# define stopwords
STOPWORDS = {
    "a", "an", "the", "and", "or", "but",
    "is", "are", "was", "were", "be", "been",
    "of", "to", "in", "on", "for", "with",
    "that", "this", "it", "as", "by",
    "at", "from", "am"
}


# extracting the text 
def extract_text(html: str) -> str:
 
    soup = BeautifulSoup(html, "html.parser")

    # Remove script and style content — not useful text
    for tag in soup(["script", "style"]):
        tag.decompose()

    return soup.get_text(separator=" ")


# tokenisation 
def tokenise(text: str) -> list[str]:

    # lowercasing all the letters
    text = text.lower()

    # remove punctuations
    tokens = re.findall(r'\b[a-z0-9]+\b', text)
    
    # remove stopwords
    tokens = [t for t in tokens if t not in STOPWORDS and len(t) > 1]

    return tokens


# build the inverted index
def build_index(pages: dict[str, str]) -> dict:

    index = {}
    # find the total number of pages
    total_pages = len(pages)

    for url, html in pages.items():

        if not html: 
            continue

        # strip HTML tags
        text = extract_text(html)

        # tokenise into clean words
        tokens = tokenise(text)

        total_tokens = len(tokens)

        if total_tokens == 0:
            continue

        # Build postings for this document 
        # Each token gets its position recorded (0-based word index)
        for position, word in enumerate(tokens):
            if word not in index:
                index[word] = {}

            if url not in index[word]:
                index[word][url] = {"frequency": 0, "positions": [], "tf_idf": 0.0}

            index[word][url]["frequency"] += 1
            index[word][url]["positions"].append(position)
    
    # using the frequencies of each word, compute TF-IDF
    for word, postings in index.items():
        # compute IDF: how rare is this word across all documents
        docs_containing_word = len(postings)
        idf = math.log(total_pages / docs_containing_word)

        for url, data in postings.items():
            total_tokens = len(tokenise(extract_text(pages[url])))
            # compute TF
            tf = data["frequency"]/total_tokens if total_tokens > 0 else 0
            data["tf_idf"] = round(tf * idf, 4)


    return index

# build command to save the index file
def save_index(index: dict, path:str) -> None:

    try:
        with open(path, "w") as f:
            json.dump(index, f, indent=2)

        print(f"[SUCCESS]: Index saved to {path} ({len(index)} terms)")
    except OSError as e:
        print(f"[ERROR] Could not save index to {path}: {e}")
        raise

# load the index from the file
def load_index(path: str)->dict:

    try: 
        with open(path, "r") as f:
            index = json.load(f)
        
        print(f" Loaded from {path} ({len(index)} terms)")
        return index
    except FileNotFoundError:
       raise FileNotFoundError(f"No index found.")





