'''This task scrapes the data from https://www.worldometers.info/coronavirus/ '''

import requests
from bs4 import BeautifulSoup
import logging as log
from Mongo import connection_client
from datetime import datetime
import numpy as np
from pandas import pandas as pd


URL = 'https://www.worldometers.info/coronavirus/'

data = dict()

# Logger setup
log.basicConfig(level=log.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M',
                    filename='../logs/scrapper.log',
                    filemode='w')


page = requests.get(URL)
soup = BeautifulSoup(page.content, 'html.parser')

def collect_total_number_data():
    '''Function collects that data from worldmeters.info'''

    try:
        items = soup.find_all('div', class_="maincounter-number")
        total_cases = float(items[0].find('span').text.strip().replace(',', ''))
        total_death = float(items[1].find('span').text.strip().replace(',', ''))
        total_recorvery = float(items[2].find('span').text.strip().replace(',', ''))

        return {"total_cases": total_cases, "total_death": total_death, "total_recorvery": total_recorvery}

    except AttributeError as e:
        log.error("AttributeError Exception occurred", exc_info=True)
    except TypeError as e:
        log.error("TypeError Exception occurred", exc_info=True)
    except:
        log.error("Exception occurred", exc_info=True)

def get_active_cases():
    ''' function extracts all the active and close cases and returns an dictionary with the data'''
    try:
        items = soup.find_all('div', class_="col-md-6")
        heading = str()
        total_active_cases = float()
        mild_condition = float()
        critical_condition = float()

        for item in items:
            # extracting header from active cases and close cases
            if item.find('div', class_="panel-heading"):
                heading = item.find('div', class_="panel-heading").text.strip().lower()

            if item.find('div', class_="panel-body"):
                total_active_cases = float(item.find('div', class_="number-table-main").text.strip().replace(',', ''))
                
                # Extraction Conditions
                conditions = item.find_all('span', class_="number-table")
                mild_condition = float(conditions[0].text.strip().replace(',', ''))
                critical_condition = float(conditions[1].text.strip().replace(',', ''))

                return { 
                    "total_active_cases": total_active_cases,
                    "mild_condition": mild_condition, 
                    "critical_condition": critical_condition
                }
                
    except AttributeError as e:
        print(e)
        log.error("AttributeError Exception occurred", exc_info=True)
    except TypeError as e:
        print(e)
        log.error("TypeError Exception occurred", exc_info=True)
    except:
        log.error("Exception occurred", exc_info=True)

def per_country_info(country_url):
    '''
        Extract data form the /country/<country_name>
        this is limited as not all country in the table has a link
    '''
    country_page = requests.get(URL+country_url)
    soup = BeautifulSoup(country_page.content, 'html.parser')

    try:
        items = soup.find_all('div', class_="maincounter-number")
        total_cases = float(items[0].find('span').text.strip().replace(',', ''))
        total_death = float(items[1].find('span').text.strip().replace(',', ''))
        total_recorvery = float(items[2].find('span').text.strip().replace(',', ''))
        return {"total_cases": total_cases, "total_death": total_death, "total_recorvery": total_recorvery}

    except AttributeError as e:
        log.error("AttributeError Exception occurred", exc_info=True)
    except TypeError as e:
        log.error("TypeError Exception occurred", exc_info=True)
    except:
        log.error("Exception occurred", exc_info=True)


def collect_country_data():
    '''Collects the data per country if country data has a link to extract'''

    country_list_info = []
    try:    
        table = soup.find('tbody')
        for row in table.find_all('tr'):
            for td in row.find('td'):
                try:
                    per_country = dict()
                    per_country['country'] = td.text.strip()
                    country_url = td['href']
                    if country_url is not None:
                        per_country['data'] = per_country_info(country_url)
                        country_list_info.append(per_country)
                    del per_country
                except AttributeError as e:
                    log.error("AttributeError Exception occurred", exc_info=True)   
    except AttributeError as e:
        log.error("AttributeError Exception occurred", exc_info=True)
    except TypeError as e:
        log.error("TypeError Exception occurred", exc_info=True)
    except:
        log.error("Exception occurred", exc_info=True)
    finally:
        return country_list_info

def clean_table_list_data(country_list_info):
    '''Use pandas to clena the data'''
    try:
        # Cleaning the data 
        columns_table=['Country', 'Total Cases','New Cases', 'Total Death', 'New Death', 'Total Recovered', 'Active Cases', 'Serious Critical', 'Total Cases / 1M pop']
        # df = pd.DataFrame(country_list_info, columns=columns_table)
        df = pd.DataFrame(country_list_info)
        df = df.replace({'\+': '', ',': ''}, regex=True)
        col = df.select_dtypes(object).columns
        df[col] = df[col].apply(pd.to_numeric, errors='ignore')
        df = df.replace(np.nan, 0)
        country_list_info = df.values.tolist()
        return country_list_info
    except:
        log.error("Exception occurred", exc_info=True)


def collect_country_from_table():
    '''Collects the data per country from table in the main page.'''
    country_list_info = []
    countries = []
    try:    
        table = soup.find('tbody')
        for row in table.find_all('tr'):
            individual_country = []
            for item in row.find_all('td'):
                individual_country.append(item.text.strip())
            country_list_info.append(individual_country)
            del individual_country

    except AttributeError as e:
        log.error("AttributeError Exception occurred", exc_info=True)
    except TypeError as e:
        log.error("TypeError Exception occurred", exc_info=True)
    except:
        log.error("Exception occurred", exc_info=True)
    finally:
        countries = clean_table_list_data(country_list_info)
        return countries

def get_data():
    '''Returns a object with all coronavirus data'''

    data.update(get_active_cases())
    data.update(collect_total_number_data())
    data['countries'] = collect_country_from_table()
    data['Date'] = str(datetime.today())

    return data

if __name__ == "__main__":
    try:
        data = get_data()
        import pprint
        pprint.pprint(data)
        db = connection_client()
        db.datos.insert_one(data)
    except:
        log.error("Exception occurred storing the data", exc_info=True)
