"""
main.py - Command Line Interface for this project

It provides an interactive shell with 4 coomands:
    build: Crawl the targeted website, build the inverted index and save to path
    load: Load the previously built inverted index
    print: print the inverted index entry for a word
    find: find all pages containing one or more words from user query

To Use:
    python src/main.py
"""

from crawler import crawl_site
from indexer import build_index, save_index, load_index
from search import print_query, find_words

INDEX_PATH = "data/index.json"
# INDEX_PATH = "data/index_main_only.json"
BASE_URL = "https://quotes.toscrape.com/"

def main() -> None:

    """
    Runs the interactive command-line search engine shell. 
    
    Accept four commands: build, load, print, find.
    Use the command 'quit' or 'exit' to stop. 

    """

    index = {}

    
    print("Simple Search Engine")
    print("Commands: build, load, print <word>, find <word> [word2 ...], quit")

    while True:
        command = input("> ").strip().split()

        if not command:
            continue

        cmd = command[0].lower()

        # build command that crawl the website, buildt the inverted index and save to the path
        if cmd == "build":
            print("Crawling website...")
            pages = crawl_site(BASE_URL)

            print("Building inverted index...")
            index = build_index(pages)

            save_index(index, INDEX_PATH)

        # load the inverted index
        elif cmd == "load":
            index = load_index(INDEX_PATH)
            print("Index loaded successfully")

        # print the inverted index entry for a given word 
        elif cmd == "print":
            if len(command) < 2:
                print("Usage: print <word>")
                continue
            if len(command) > 2:
                print(f"[WARNING] print command only accepts one word. Showing results for '{command[1]}' only.")
            print_query(index, command[1])

        # find all the pages containing the words
        elif cmd == "find":
            if len(command) < 2:
                print("Usage: find <word> [word2 ...]")
                continue

            results = find_words(index, command[1:])

            if results:
                for url in results:
                    print(url)
            else:
                print("No matching pages found.")
        
        # quite the interactive shell
        elif cmd in {"exit", "quit"}:
                    print("Bye.")
                    break
        
        else:  
            print(f"Unknown command: {cmd}")


if __name__ == "__main__":
    main()




























