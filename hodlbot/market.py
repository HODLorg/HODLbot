#!/usr/bin/python
import logging
import requests
import json

from pprint import pprint
from time import time, sleep

log = logging.getLogger(__name__)

def request_market():
    try:
        response = requests.get("https://api.coinmarketcap.com/v1/ticker/?limit=10")
        data = json.loads(response.content)

        # Convert data json into dict
        log.debug("Data obtained from web source.")
        market = {
            'crypto_currencies': {},
            'last_updated': int(time())
        }
        for d in data:
            currency_dict = {
                'name': str(d['name']),
                'price_btc': float(d['price_btc']),
                'price_usd': float(d['price_usd']),
                'rank': int(d['rank']),
                'symbol': str(d['symbol']),
                'last_updated': int(d['last_updated'])
            }
            currency_key = str(d['id'])
            market['crypto_currencies'][currency_key] = currency_dict

        # Output collected data into file
        with open('data/market.json', 'w') as f:
            json.dump(market, f, sort_keys=True, indent=4)
    except Exception as e:
        log.error("Exception in requesting market: {}".format(e))
        log.warning("No data from web source. Loading file")
        # Get last data from file
        with open('data/market.json', 'r') as f:
            market = json.load(f)

    return market
