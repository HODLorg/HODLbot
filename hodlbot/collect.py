#!/usr/bin/python
import logging
import requests
import json

from pprint import pprint
from time import sleep

log = logging.getLogger(__name__)

def collect_data():
    response = requests.get("https://api.coinmarketcap.com/v1/ticker/?limit=10")
    data = json.loads(response.content)

    # Convert data json into dict
    data_dict = {}
    for d in data:
        key = d['id']
        data_dict[key] = d

    # Output collected data into file
    with open('data/market.json', 'w') as f:
        json.dump(data_dict, f, sort_keys=True, indent=4)

    return data_dict
