import requests


def get_license_keys(response_json):
    """
    Get license keys from a single dejacode page using API
    """
    results = response_json['results']
    keys = [result.get('key') for result in results]
    return keys


def get_all_license_keys(api_url, headers):
    all_license_keys = []

    while api_url:
        response = requests.get(api_url, headers=headers)
        print 'fetching %s' % api_url
        response_json = response.json()
        # gets license keys for each page and add to keys list
        all_license_keys += get_license_keys(response_json)
        api_url = response_json.get('next')
        print all_license_keys
    return all_license_keys


api_url = ''
headers = {'Authorization': 'Token '}

print get_all_license_keys(api_url, headers)
