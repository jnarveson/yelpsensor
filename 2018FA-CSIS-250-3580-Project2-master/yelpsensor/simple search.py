import pprint
from urllib.parse import quote
import requests


API_KEY = 'pacc4ghRE-bYl6Y6S45N9RHn2ElT5DyCJMbesOU8mYiVuMNx1tReWqsg6CcD5yK3tY8etGwvRwYipANjPStUDr_Rk_jZT2BAqc2Wkelf2Xu79IXR-TWjR4luBczgW3Yx'
API_HOST = 'https://api.yelp.com'
SEARCH_URL = '/v3/businesses/search'
BUSINESS_URL = '/v3/businesses/'


def request(host, path, url_params=None):
    """Makes a request to Yelp's API"""
    url_params = url_params or {}
    url = '{0}{1}'.format(host, quote(path))
    headers = {'Authorization': 'Bearer %s' % API_KEY}
    print('Searching', url, " ...")
    response = requests.request('GET', url, headers=headers, params=url_params)
    return response.json()


def get_info(term, location):
    """Gets info about the businesses that turn up in the user's search request"""
    parameters = {'term': term.replace(' ', '+'), 'location': location.replace(' ', '+'), 'limit': 1}
    query = request(API_HOST, SEARCH_URL, parameters)
    businesses = query.get('businesses')
    business_id = businesses[0]['id']
    print("Top result found: ", business_id,)
    details = get_ID(API_KEY, business_id)
    print("Results for business: ", business_id, ":\n")
    pprint.pprint(details, indent=1)


def get_ID(API_KEY, business_id):
    """Gets info about businesses by business ID"""
    business_path = BUSINESS_URL + business_id
    return request(API_HOST, business_path, API_KEY)

def main():

    term = 'restaurant'
    location = 'El Cajon'
    get_info(term, location)


if __name__ == '__main__':
    main()
