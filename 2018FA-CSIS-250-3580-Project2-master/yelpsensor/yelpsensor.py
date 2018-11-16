import pprint
from urllib.parse import quote
import os
import time
import logging
import requests
from datetime import datetime, timezone
from requests import Timeout, HTTPError, ConnectionError
from sensor import SensorX

API_KEY = 'pacc4ghRE-bYl6Y6S45N9RHn2ElT5DyCJMbesOU8mYiVuMNx1tReWqsg6CcD5yK3tY8etGwvRwYipANjPStUDr_Rk_jZT2BAqc2Wkelf2Xu79IXR-TWjR4luBczgW3Yx'
API_HOST = 'https://api.yelp.com'
SEARCH_URL = '/v3/businesses/search'
BUSINESS_URL = '/v3/businesses/'

__CONFIG_FILE = 'yelpSensor.json'

logging.basicConfig(
    level=logging.INFO,
    filename=os.path.join(os.getcwd(), 'logs', 'yelpsensor.log'),
    filemode='a',
    format='%(asctime)s - %(lineno)d - %(message)s')


class YelpSensor(SensorX):

    def __init__(self):
        """ calling the super this a file name, without extension """
        super().__init__(os.path.join(os.path.dirname(__file__), self.__class__.__name__))
        logging.info("Sensor just woke up .. ready to be called")

    def get_all(self):
        """ return fresh or cached content"""
        if self._request_allowed():
            return self._fetch_data()
        else:
            return self._read_buffer()

    def _fetch_data(self):
        """ json encoded response from webservice .. or none"""
        try:
            response = requests.get(self.props['service_url'] % (
                50, self.props['city'], self.props['countrycode'], self.props['units'], self.props['apikey']))
            self.props['last_used'] = int(time.time())
            self._save_settings()  # remember time of the last service request
            if response.status_code == 200:
                content = self._create_content(response.json())
                logging.info("successfully requested new content")
                self._write_buffer(content)  # remember last service request(s) results.
            else:
                logging.warning("response: {} {} {}".format(response.status_code, response, response.text))
                content = None
        except (HTTPError, Timeout, ConnectionError, KeyError, ValueError, TypeError) as e:
            logging.error("except: " + str(e))
            content = None
        return content

    def get_featured_image(self):
        return self.props['featured_image']

    @staticmethod
    def _create_content(ws_json):
        """ convert the json response from the web-service into a list of dictionaries that meets our needs. """
        if ws_json['cod'] == '200':
            m = max(ws_json['list'], key=lambda item: int(item['main']['temp_max']))
            ts0 = datetime.now()
            tsx = datetime.fromtimestamp(m['dt'])
            d = {'k': ts0,
                 'date': ts0.strftime('%Y-%m-%d %I:%M:%S %p'),
                 'caption': 'Temperature forecast for Grossmont College',
                 'summary': 'For Grossmont College, the warmest temperature of **{} F** is forecast for {}'.format(
                     m['main']['temp_max'], tsx.strftime("%A %I:%M:%S %p"))
                 }
            return [d]
        return []


def search(host, path, url_params=None):

    url_params = url_params or {}
    url = '{0}{1}'.format(host, quote(path))
    headers = {'Authorization': 'Bearer %s' % API_KEY}
    print('Searching', url, " ...")
    response = requests.request('GET', url, headers=headers, params=url_params)
    return response.json()


def get_info(term, location):

    parameters = {'term': term.replace(' ', '+'), 'location': location.replace(' ', '+'), 'limit': 1}
    query = search(API_HOST, SEARCH_URL, parameters)
    businesses = query.get('businesses')
    business_id = businesses[0]['id']
    print("Top result found: ", business_id,)
    business_path = BUSINESS_URL + business_id
    response = search(API_HOST, business_path)
    print("Results for business: ", business_id, ":\n")
    pprint.pprint(response, indent=1)


def main():

    term = 'bar'
    location = 'El Cajon'
    get_info(term, location)


if __name__ == '__main__':
    main()

