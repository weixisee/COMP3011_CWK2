from crawler import crawl_site
from indexer import build_index, save_index, load_index
from search import print_query, find_words

INDEX_PATH = "data/index.json"
# INDEX_PATH = "data/index_main_only.json"
BASE_URL = "https://quotes.toscrape.com/"

def main():

    index = {}

    
    print("Simple Search Engine")
    print("Commands: build, load, print <word>, find <word> [word2 ...], quit")

    while True:
        command = input("> ").strip().split()

        if not command:
            continue

        cmd = command[0].lower()

        
        if cmd == "build":
            print("Crawling website...")
            pages = crawl_site(BASE_URL)

            print("Building inverted index...")
            index = build_index(pages)

            save_index(index, INDEX_PATH)

        
        elif cmd == "load":
            index = load_index(INDEX_PATH)
            print("Index loaded successfully")

        
        elif cmd == "print":
            if len(command) < 2:
                print("Usage: print <word>")
                continue

            print_query(index, command[1])

        
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
        
        
        elif cmd in {"exit", "quit"}:
                    print("Goodbye.")
                    break
        
        else:  
            print(f"Unknown command: {cmd}")


if __name__ == "__main__":
    main()




























