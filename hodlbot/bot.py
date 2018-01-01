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

        self.__initialize_portfolio()

    @staticmethod
    def get_market():
        log.debug("Getting current Market data.")
        return collect_data()

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
            initial_investment_fiat = self.__config['initial_fiat_investment'] / 10.0
            log.debug("Initial fiat investment for {}: {} USD".format(cc, initial_investment_fiat))
            initial_investment = float(self.__market[cc]['price_usd']) * initial_investment_fiat
            log.debug("Initial investment for {}: {} {}".format(cc, initial_investment, self.__market[cc]['symbol']))
            initial_investment_btc = float(self.__market[cc]['price_btc']) * initial_investment
            log.debug("Initial investment value for {} in Bitcoin: {} BTC".format(cc, initial_investment_btc))

            portfolio[cc] = {
                'name': cc,
                'symbol': self.__market[cc]['symbol'],
                'main_currency': self.__is_main_currency(self.__market[cc]),
                'investment_fiat': initial_investment_fiat,
                'investment': initial_investment,
                'investment_btc': initial_investment_btc
            }

        with open("data/portfolio.json", 'w') as f:
            json.dump(portfolio, f, sort_keys=True, indent=4)

    def __market_updater(self):
        while True:
            self.__market = self.get_market()
            log.debug("Market updated.")
            sleep(30)

    def __run(self):
        while True:
            log.debug("HODLbot running.")
            sleep(5)
