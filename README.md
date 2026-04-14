# COMP3011 Coursework 2 - Search Engine Tool
## Project Overview
This project involves building a simple search engine tool that crawls the Quotes to Scrape website at https://quotes.toscrape.com/

## Set Up Instructions

### Prerequisites
- Python 3.10+

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

**load**

The load command is used to load the index from the saved file.

**print <word>**

The print command will print the index for a given word. It will return the page that contains the words with its frequency and positions. 

**find <word> [word2...]**

The find command will find all pages that contains the given words. It will return a list of all pages that includes the query. For multi-word queries, only the command pages that contains all the words will be returned. 

### Testing
The tests are written using **pytest**

To run the test, run the following command in project root
```bash
pytest
```
