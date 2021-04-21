# gofundme WebScraper

To install dependencies:
pip install -r requirements.txt

To run code:
python Scraper.py

This will run with the search words: Venezuela Covid and go through as many search pages as possible before saving a pickled dataframe.

To run with different search terms:
python Scraper.py --query-terms UK sports club

To limit the number of search pages:
python Scraper.py --page-limit 5

This will limit the search to the first 5 pages.



