# gofundme WebScraper

To install dependencies:
pip install -r requirements.txt
____

To run the code:

`python Scraper.py`

The deault arguments are to search for Venezuela & Covid and go through as many search pages as possible before saving a pickled dataframe.

___

To run with different search terms:

`python Scraper.py --query-terms UK sports club`

To limit the number of search pages to the first 5 pages:

`python Scraper.py --page-limit 5`



