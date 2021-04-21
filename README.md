# gofundme WebScraper

To install dependencies:

`pip install -r requirements.txt`

After instlaling the dependencies you'll need to download the executable for the Selenium Browser.

In this code we are using Geckodriver (Mozilla firefox). This can be downloaded from [here](https://github.com/mozilla/geckodriver/releases). Once you have downloaded the file that matches your operating system, unzip it:
- Linux, `tar -xf file.tar.gz`
- Mac OS, unzip by double clicking
- Windows, winrar or similar. 

After you have extratced the contents, move the executable file called `geckodriver` into the repository.

____

To run the code:

`python Scraper.py`

The deault arguments are to search for Venezuela & Covid and go through as many search pages as possible before saving a pickled dataframe.

___

To run with different search terms:

`python Scraper.py --query-terms UK sports club`

To limit the number of search pages to the first 5 pages:

`python Scraper.py --page-limit 5`



