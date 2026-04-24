# COMP3011 Coursework 2 - Search Engine Tool
## Project Overview
This project involves building a command-line search engine tool that crawls the Quotes to Scrape website at https://quotes.toscrape.com/, builds an inverted index and allows users to find the words across all the scraped pages. 

**Key Features**
1. Full website crawler that respects that 6s politeness window between each requests and complies to the robots.txt file
2. Build an inverted index that stores the term's frequency, positions in the page and the TF-IDF score
3. Utilise TF-IDF scoring
4. Query suggestions for misspelled word using difflib
5. 99% test coverage across 70 tests

## Architecture Overview
```
COMP3011_CWK2/
├── src/
│   ├── crawler.py
│   ├── indexer.py
│   ├── search.py
│   └── main.py
├── tests/
│   ├── test_crawler.py
│   ├── test_indexer.py
│   └── test_search.py
├── data/
│   └── index.json
├── requirements.txt
└── README.md
```

## Set Up Instructions

### Prerequisites
- Python 3.10+

### Dependencies
- requests
- beautifulsoap4
- pytest
- pytest-cov

### 1. Clone the repository
```bash
git clone https://github.com/weixisee/COMP3011_CWK2.git
cd COMP3011_CWK2
```

### 2. Set up virtual environment
```bash
python -m venv venv
```
### 3. Activate virtual environment
   
**Windows**
```bash
venv\Scripts\activate
```

**macOS/Linux**
```bash
source venv/bin/activate
```

### 4. Install dependencies
```bash
pip install -r requirements.txt
```

### 5. Run the application
```bash
python src/main.py
```


### Usage
There are **four** available commands, including build, load, print <word> and find <word>

**build**

The build command is used to crawl the targeted website, build the index and save the results in data/index.json file. 
```
> build
Crawling website...
[CHECKING]: robots.txt loaded from https://quotes.toscrape.com/

Fetching: https://quotes.toscrape.com/
[POLITENESS] Waiting 6s.

Fetching: https://quotes.toscrape.com/login
[POLITENESS] Waiting 6s.
```

**load**

The load command is used to load the previously built index from data/index.json. Build command must run before this.

```
> load 
 Loaded from data/index.json (4486 terms)
Index loaded successfully
```

**print <word>**

The print command will print the index for a given word. It will return the page that contains the words with its frequency and positions. It is ranked based on the TF-IDF score.

```
> print integrity
URL: https://quotes.toscrape.com/page/9/
Frequency: 1
Positions: [75]

URL: https://quotes.toscrape.com/tag/integrity/page/1/
Frequency: 2
Positions: [7, 44]
```

```
> print nonexistent
[ERROR]: Could not find 'nonexistent' in index. Did you mean: 'consistent'?
```

**find <word> [word2...]**

The find command will find all pages that contains the given words. It will return a list of all pages that includes the query. For multi-word queries, only the pages that contains all the words will be returned. 

```
> find integrity
https://quotes.toscrape.com/tag/integrity/page/1/
https://quotes.toscrape.com/page/9/
```

```
> find good friends
https://quotes.toscrape.com/tag/contentment/page/1/
https://quotes.toscrape.com/tag/good/page/1/
https://quotes.toscrape.com/tag/aliteracy/page/1
```

```
> find llife
[ERROR]: Could not find 'llife'. Did you mean: 'life'?

No matching pages found.
````

### Testing
The tests are written using **pytest**

To run the test, run the following command in project root
```bash
pytest tests/ -v
```

### Testing Strategy
- Unit Test - tested each function independently with mock data
- Integration Test - tested the whole pipeline to ensure all components work together (build, save, load, print/find)
- Edge Case Test - Tested edge cases such as empty string or empty page, special characters, single characters
- Mocking - Used unittest.mock to mock HTTP requests to make sure no real network calles during testing stage


