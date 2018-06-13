import pandas as pd
import re
import csv
import errno
from bs4 import BeautifulSoup
from restaurent.constants import CHROME_DRIVER, RestaurentConstants
from selenium import webdriver
from socket import errno as SocketError
import time

path_to_chromedriver = CHROME_DRIVER


class RestaurentDetail:

    def restaurents_data(self):
        """
        write url, name, address and rating of a restaurent in csv file
        """
        file = RestaurentConstants.DATA_WITHOUT_REVIEW
        f = open(file, 'w')
        headers = (
            'Url,Name,Address,Rating'
            '\n')
        f.write(headers)
        for i in range(1, 593):
            driver = webdriver.Chrome(executable_path=path_to_chromedriver)
            driver.implicitly_wait(10)
            try:
                url = (
                    'https://www.zomato.com/bangalore/restaurants?page={}'.
                    format(i))
                driver.get(url)

                soup = BeautifulSoup(driver.page_source, 'html.parser')
                contents = soup.findAll('div', {'class': 'content'})
            except SocketError as e:
                if e.errno != errno.ECONNRESET:
                    raise Exception
                pass
            time.sleep(1)
            driver.quit()
            for content in contents:
                links = content.find_all("a", {"class": "result-title"})
                for link in links:
                    url = link.get('href', None).replace(
                        '\t', '').replace('\n', '').replace(',', ' ')

                    name = link.text.replace(
                        '\t', '').replace('\n', '').replace(
                        ',', ' ').replace('  ', '')

                location = content.findAll(
                    'div',
                    {'class':
                        'col-m-16 search-result-address grey-text nowrap ln22'}
                )
                for val in location:
                    address = val.text.replace(
                        '\t', '').replace('\n', '').replace(',', ' ')

                ratings = content.findAll(
                    'div',
                    {'class': (
                        'ta-right floating search_result_rating'
                        ' col-s-4 clearfix')}
                )
                for rate in ratings:
                    rating = rate.div.text.replace(
                        '\t', '').replace('\n', '').replace(',', ' ')

                    f.write(
                        url + ',' + name + ',' + address + ',' +
                        rating + '\n'
                    )

    def get_url_from_csv(self):
        """
        read the url from csv and return a list of urls
        """
        with open(RestaurentConstants.DATA_WITHOUT_REVIEW, 'r') as csvfile:
            reader = csv.DictReader(x.replace('\0', '') for x in csvfile)
            urls = []
            for row in reader:
                urls.append(row['Url'])
            return urls

    def restaurent_review_data(self):
        """
        create csv with restaurent name and review
        """
        urls = self.get_url_from_csv()
        file = RestaurentConstants.RES_REVIEW_CSV
        f = open(file, 'w')
        headers = ('Name,Review''\n')
        f.write(headers)
        for url in urls:
            driver = webdriver.Chrome(executable_path=path_to_chromedriver)
            driver.implicitly_wait(10)
            try:
                driver.get(url)
            except SocketError as e:
                if e.errno != errno.ECONNRESET:
                    raise Exception
                pass
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            time.sleep(1)
            driver.quit()
            contents = soup.findAll('a', {'class': 'ui large header left'})
            name = contents[0].text.replace(
                '\t', '').replace('\n', '').replace(',', ' ').replace('  ', '')
            review_list = soup.findAll('div', {'class': 'zs-following-list'})
            for reviews in review_list:
                sm_review = reviews.findAll(
                    'div', {'class': 'rev-text mbot0 '})
                small_review = []
                for index, val in enumerate(sm_review):
                    small_review.extend(
                        (index, val.text.replace('\t', '').replace(
                            '\n', '').replace(',', ' ').encode(
                            'ascii', 'ignore').decode("utf-8").replace(
                            'Rated', '').replace('  ', '')))

            rev = " ".join(str(x) for x in small_review)
            review = re.sub('[^a-zA-Z0-9-_*.]', ' ', rev)
            f.write(name + ',' + review + '\n')

    def merge_csv(self):
        """
        merger both csv files(without review file and with review file)
        """
        a = pd.read_csv(RestaurentConstants.DATA_WITHOUT_REVIEW)
        b = pd.read_csv(RestaurentConstants.RES_REVIEW_CSV)
        merged = a.merge(b, on='Name')
        merged.to_csv(RestaurentConstants.DATA_WITH_REVIEW, index=False)

    def process_scrap(self):
        """
        aggregator function which call all the function and final output as
        a csv with all details. But it will take lot of time to complete full
        process
        """
        self.restaurents_data()
        self.restaurent_review_data()
        self.merge_csv()
