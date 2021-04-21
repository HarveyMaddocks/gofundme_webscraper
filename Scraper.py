from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup

from datetime import date
import re
import pandas as pd
import requests
import argparse


def set_args():
    """
    Define a list of search terms that will be used for the script
    Define an integer to limit the search pages to
    :return: parser.parse_args
    """
    # Initialise argparse object
    parser = argparse.ArgumentParser(description='Set some arguments for our script')
    # Add some arguments, elements are: short form name, long form name, type of input expected
    # default value if you don't set an argument, help string (shown if you run with --help)
    # nargs is so that we can define multiple values for a single argument

    parser.add_argument('-q', '--query-terms', type=str, default='Venezuela Covid',
                        help='list of strings to search for', nargs='*')

    parser.add_argument('-p', '--page-limit', type=int,
                        help='number to limit search pages to')

    # set the argument parser and return
    args = parser.parse_args()
    return args


def setup_selenium():
    """
    Create an instance of the selenium virtual browser the executable should be located in the same place as the script
    Virtual browser is run in headless mode so it won't be visible on the screen
    :return: driver
    """
    # Define the options to run with headless mode enabled
    options = Options()
    options.headless = True

    # Instatiate the browser object here, pointing at an exectable location which should be located in the same
    # base directory as the script
    driver = webdriver.Firefox(options=options, executable_path='./geckodriver')

    # Impicit wait tell the browser to wait up to 30s for an object to appear, this helps if the connection is slow.
    driver.implicitly_wait(30)
    return driver


def format_url(search_terms):
    """
    Formats the search terms correctly, they should be defined in the arguments to the script
    :param search_terms: str of all terms from args
    :return: str
    """
    base_url = 'https://www.gofundme.com/s?q='
    base_url += search_terms.replace(' ', '+')
    return base_url


def get_fundraiser_urls_from_page(driver):
    """
    Finds URLs of all fundraiser campaigns on the search page returns them as a list
    :param driver: browser object
    :return: List
    """
    fund_links = []
    # Use the selenium find_elements function to search for specific objects.
    # The argument for the function can be found be interrogating the source of the website
    elems = driver.find_elements_by_xpath("/html/body/div[2]/div/div[3]/div/div[1]/div/div/div")

    # only execute the code if the above line returns something.
    if len(elems) > 0:
        for elem in elems:
            # Get all the html code for the object
            elem_html = elem.get_attribute('innerHTML')

            # Then Parse using BeautifulSoup
            soup = BeautifulSoup(elem_html, 'lxml')

            # Find all link like objects of a specific class, the class type can be found be interrogating the sites
            # source code.

            for link in soup.findAll('a', {'class': 'a-link a-link--unstyled'}):
                # Check if there is a 'href' (a URL) if not skip to the next iteration
                try:
                    fund_links.append(link['href'])
                except KeyError:
                    pass

    return fund_links


def get_data_from_page(url):
    """
    Parse the URl with beautiful soup and using predefined routines extract all the information that we want.
    :param url:
    :return: Dict
    """
    # Initialise a dictionary to store our information
    row = {'url': url}

    # get the html content of a website using the requests library and the get function
    # the '.content' returns the contents of the request, without it would return the HTTP status code
    page_contents = requests.get(url).content

    # parse the contents with beautiful soup
    soup = BeautifulSoup(page_contents, 'lxml')

    # Get the text relating to the campaign title which belong to that specific class.
    for element in soup.find_all(class_="a-campaign-title"):
        row['title'] = element.text

    # Interrogating the source we found that the tags are URLs that always contain the 'discover' path
    # So we just need to find all the URLs that contain that string and return them
    tags = []
    for link in soup.find_all('a', href=True):
        if 'discover' in link['href']:
            tags.append(link.text)

    row['tags'] = tags

    # Progress meter is a single string in this class.
    for link in soup.findAll('h2', {'class': 'm-progress-meter-heading'}):
        goal = link.text

        # The format is strictly defined so we can do some string parsing to get the information we want
        row['current amount'] = goal.split()[0]
        row['total_amount'] = goal.split()[-2]

    for link in soup.findAll('div', {'class': 'p-campaign-description'}):
        row['description'] = link.text

    for link in soup.findAll('span', {'class': 'm-campaign-byline-created a-created-date'}):
        row['created'] = link.text

    # Some information exists only in the footer of the "donations" page, which is summarised in the side bar
    # We can't access it directly but the page URL is well formated so we can use some string manipulation to create
    # the URL and parse it.

    # the gofundme URLs are well formated along the lines of www.gofundme.com/f/name of fundraiser?qidSOMEHEXCODE
    # We can use the '?qid' as an anchor and replace it with '/donations?qid' to get the URL of the donations page
    donations_url = url.replace('?qid', '/donations?qid')

    soup = BeautifulSoup(requests.get(donations_url).content, 'lxml')
    text_soup = str(soup)

    # The information in this section is outside of the usual html format, but it is well structured
    # We can extract it using regular expressions that look for the information
    for dates in re.findall('launch_date\":\"[0-9-]+', text_soup):
        row['launch_date'] = dates.rsplit('"', 1)[-1]

    for country in  re.findall('country\":\"[A-Z]+', text_soup):
        row['country'] = country.rsplit('"', 1)[-1]

    for donation_count in re.findall('donation_count\":[0-9]+', text_soup):
        row['donation_count'] = donation_count.rsplit(':', 1)[-1]

    for charity in re.findall('charity\":[a-z]+', text_soup):
        row['is_charity'] = charity.rsplit(':', 1)[-1]

    return row


def main():
    # Get our arguments
    args = set_args()

    # Define the URL with the search terms included
    url = format_url(args.query_terms)

    # Print to cmd line for debugging
    print(url)

    # Initialise our virtual browser
    driver = setup_selenium()

    # Set an emmpty list to receive data
    data = []

    # First page, this will be our iterator
    page_n = 1
    stop_condition = True

    # Start a while loop, it depends on the page number being less than the limit set in the arguments
    # or until it finds a page with no fund links
    while stop_condition:
        # check if the page_number is greater than one
        # search page syntax starts on page 2
        if page_n > 1:
            next_url = url + '&pg='+str(page_n)
        else:
            next_url = url

        # Check if page_limit was set, then if it was check if page number is equal to it, if this condition is met
        # the while loop will end
        if args.page_limit:
            if page_n == args.page_limit:
                stop_condition = False
        # Advance page number iterator
        page_n += 1

        # Retrieve the next page in the browser
        driver.get(next_url)

        # Pass the browser instance into this function to return all the fundraiser links
        fund_links = get_fundraiser_urls_from_page(driver)

        # check if there were some fundraisers found, if not the while loop will end.
        if len(fund_links) > 0:
            for fund in fund_links:

                # format the fundraiser url then pass it to the next function to retrieve the desired infromation
                # This gets appended to the list at the start.
                page_link = 'https://www.gofundme.com' + fund
                print(page_link)
                data.append(get_data_from_page(page_link))
        else:
            stop_condition = False

    # Get todays date
    today = date.today()

    # File name for saving the dataframe, includes the search terms (seperated by a _) and the date on which it was run
    f_name = 'GoFundMeData_' + args.query_terms + '_' + today.strftime('%Y%m%d')
    if args.page_limit:
        f_name += '_'+str(args.page_limit)

    f_name += '.pkl'

    # convert list of dicts to pandas dataframe
    df = pd.DataFrame(data)

    # Save the dataframe with pickle, this has a compression factor so it won't take up so much space
    # to open again df = pd.DataFrame.from_pickle(f_name)
    df.to_pickle(f_name)

    # Print filename to cmd line
    print('Data Saved to:', f_name)

    # Stop selenium client and shut it down gracefully
    driver.stop_client()
    driver.quit()


if __name__ == '__main__':
    main()
