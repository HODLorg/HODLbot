#!/usr/bin/python

import threading
import logging
import json

from time import sleep
from pprint import pprint

from collect import collect_data

log = logging.getLogger(__name__)

class HODLbot:
    def __init__(self, config):
        self.__config = config
        self.__threads = []
        self.__market = self.get_market()

        self.__portfolio = self.__initialize_portfolio()

    @staticmethod
    def get_market():
        log.debug("Getting current Market data.")
        return collect_data()

    @staticmethod
    def summarize_portfolio(portfolio, market):
        total_value_fiat = 0
        for cc in portfolio:
            if type(portfolio[cc]) is dict: # Check if CC
                total_value_fiat = total_value_fiat + portfolio[cc]['investment'] * float(market[cc]['price_usd'])

        return total_value_fiat


    def start(self):
        log.info("Starting HODLbot...")
        log.debug("Creating threads.")
        t_market_updater = threading.Thread(name="MarketUpdater", target=self.__market_updater)
        t_market_updater.daemon = True
        self.__threads.append(t_market_updater)
        t_run_bot = threading.Thread(name="HODLbot", target=self.__run)
        t_run_bot.daemon = True
        self.__threads.append(t_run_bot)

        log.debug("Starting threads.")
        t_market_updater.start()
        t_run_bot.start()

        log.debug("Threads started: {}".format(self.__threads))
        return True

    def __is_main_currency(self, currency):
        is_main_currency = True if currency['symbol'] is self.__config['main_cc'] else False

        return is_main_currency

    def __initialize_portfolio(self):
        portfolio = {}
        try:
            with open("data/portfolio.json", 'r') as f:
                log.info("Existing portfolio found.")
                return json.load(f)

        except IOError:
            log.warning("No portfolio found.")
            log.info("Creating new portfolio based on configuration.")

        # Create a new portfolio and save it.
        for cc in self.__market:
            if self.__market[cc]['symbol'] == self.__config['main_cc']:
                is_main_currency = True
            else:
                is_main_currency = False

            initial_investment_fiat = self.__config['initial_fiat_investment'] / 10.0
            log.debug("Initial fiat investment in {}: {} USD".format(cc, initial_investment_fiat))
            initial_investment = initial_investment_fiat / float(self.__market[cc]['price_usd'])
            log.debug("Initial investment in {}: {} {}".format(cc, initial_investment, self.__market[cc]['symbol']))
            initial_investment_btc = initial_investment * float(self.__market[cc]['price_btc'])
            log.debug("Initial investment in {}: {} BTC".format(cc, initial_investment_btc))

            portfolio[cc] = {
                'name': cc,
                'symbol': self.__market[cc]['symbol'],
                'main_cc': is_main_currency,
                'investment_fiat': initial_investment_fiat,
                'investment': initial_investment,
                'investment_btc': initial_investment_btc
            }


        total_value_fiat = self.__config['initial_fiat_investment']
        total_value_btc = self.__config['initial_fiat_investment'] / float(self.__market['bitcoin']['price_usd'])
        log.debug("Initial total fiat investment: {} USD".format(total_value_fiat))
        log.debug("Initial total investment: {} BTC".format(total_value_btc))
        portfolio['total_value_fiat'] = total_value_fiat
        portfolio['total_value_btc'] = total_value_btc

        with open("data/portfolio.json", 'w') as f:
            json.dump(portfolio, f, sort_keys=True, indent=4)

        return portfolio

    def __market_updater(self):
        while True:
            self.__market = self.get_market()
            log.debug("Market updated.")
            sleep(30)

    def __run(self):
        while True:
            log.debug("HODLbot running.")
            print(self.summarize_portfolio(self.__portfolio, self.__market))
            sleep(5)
