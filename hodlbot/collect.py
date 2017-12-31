#!/usr/bin/python

import requests
import json

from pprint import pprint
from time import sleep

def collect_data():
    response = requests.get("https://api.coinmarketcap.com/v1/ticker/?limit=10")
    data = json.loads(response.content)

    #pprint(data)

    # Convert data json into dict
    data_dict = {}
    for d in data:
        key = d['id']
        data_dict[key] = d

    #pprint(data_dict)

    # Output collected data into file
    with open('data/market.json', 'w') as f:
        json.dump(data_dict, f, sort_keys=True, indent=4)

    # Test the Output
    #with open('data/market.json', 'r') as f:
    #    pprint(json.loads(f.read()))
