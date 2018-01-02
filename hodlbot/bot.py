#!/usr/bin/python

import threading
import logging
import json

from time import time, sleep
from pprint import pprint

from market import request_market

log = logging.getLogger(__name__)

class HODLbot:
    def __init__(self, config):
        self.__config = config
        self.__threads = []

        self.__market = request_market()
        self.__portfolio = self.__initialize_portfolio()
        self.__trades = []

    @staticmethod
    def get_market():
        return self.__market

    @staticmethod
    def get_portfolio():
        return self.__portfolio

    @staticmethod
    def evaluate_portfolio(portfolio, market):
        total_value_fiat = 0
        total_value_btc = 0
        total_initial_investment_fiat = 0
        for cc in portfolio['crypto_currencies']:
            value_fiat = portfolio['crypto_currencies'][cc]['investment'] * market['crypto_currencies'][cc]['price_usd']
            value_btc = portfolio['crypto_currencies'][cc]['investment'] * market['crypto_currencies'][cc]['price_btc']
            gain_percentage = (value_fiat / portfolio['crypto_currencies'][cc]['initial_investment_fiat'] - 1) * 100
            portfolio['crypto_currencies'][cc].update({
                'value_fiat': value_fiat,
                'value_btc': value_btc,
                'gain_percentage': gain_percentage
            })

            total_value_fiat += value_fiat
            total_value_btc += value_btc
            total_initial_investment_fiat +=  portfolio['crypto_currencies'][cc]['initial_investment_fiat']


        total_gain_percentage = (total_value_fiat / total_initial_investment_fiat - 1) * 100

        portfolio['total_value_fiat'] = total_value_fiat
        portfolio['total_value_btc'] = total_value_btc
        portfolio['total_gain_percentage'] = total_gain_percentage

        portfolio['last_updated'] = int(time())

        log.debug("Total portfolio value: {:.2f} USD or {:.6f} BTC".format(total_value_fiat, total_value_btc))

        return portfolio

    def start(self):
        log.info("Starting HODLbot...")
        log.debug("Creating threads.")
        t_market_updater = threading.Thread(name="MarketUpdater", target=self.__MarketUpdater)
        t_market_updater.daemon = True
        self.__threads.append(t_market_updater)
        t_portfolio_updater = threading.Thread(name="PortfolioUpdater", target=self.__PortfolioUpdater)
        t_portfolio_updater.daemon = True
        self.__threads.append(t_portfolio_updater)
        t_run_bot = threading.Thread(name="HODLbot", target=self.__Run)
        t_run_bot.daemon = True
        self.__threads.append(t_run_bot)
        t_trader = threading.Thread(name="Trader", target=self.__Trader)
        t_trader.daemon = True
        self.__threads.append(t_trader)
        t_ticker = threading.Thread(name="Ticker", target=self.__Ticker)
        t_ticker.daemon = True
        self.__threads.append(t_ticker)

        log.debug("Starting threads.")
        t_market_updater.start()
        t_portfolio_updater.start()
        t_run_bot.start()
        t_trader.start()
        t_ticker.start()

        log.debug("Threads started: {}".format(self.__threads))
        return True

    def __is_main_currency(self, currency):
        is_main_currency = True if currency['symbol'] == self.__config['main_cc'] else False

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
        total_value_fiat = self.__config['total_initial_investment_fiat']
        total_value_btc = self.__config['total_initial_investment_fiat'] / self.__market.get('crypto_currencies', {}).get('bitcoin', {}).get('price_usd', 0)

        portfolio['crypto_currencies'] = {}
        for cc in self.__market.get('crypto_currencies', {}):
            name = self.__market.get('crypto_currencies', {}).get(cc, {}).get('name', '')
            symbol = self.__market.get('crypto_currencies', {}).get(cc, {}).get('symbol', '')
            is_main_cc = self.__is_main_currency(self.__market.get('crypto_currencies', {}).get(cc, {}))
            initial_investment_fiat = self.__config['total_initial_investment_fiat'] / 10.0
            log.info("Initial fiat investment in {}: {:.2f} USD".format(name, initial_investment_fiat))
            initial_investment = initial_investment_fiat / self.__market.get('crypto_currencies', {}).get(cc, {}).get('price_usd', 0)
            log.info("Initial investment in {}: {:.6f} {}".format(name, initial_investment, symbol))
            value_fiat = initial_investment_fiat
            value_btc = initial_investment * self.__market.get('crypto_currencies', {}).get(cc, {}).get('price_btc', 0)
            log.info("Initial value of {} in Bitcoin: {:.6f} BTC".format(name, value_btc))

            portfolio['crypto_currencies'][cc] = {
                'name': name,
                'symbol': symbol,
                'main_cc': is_main_cc,
                'initial_investment': initial_investment,
                'initial_investment_fiat': value_fiat,
                'investment': initial_investment,
                'value_fiat': value_fiat,
                'value_btc': value_btc,
                'value_fiat_at_last_trade': value_fiat,
                'gain_percentage': 0,
                'last_change': int(time())
            }

        log.info("Initial total fiat investment: {:.2f} USD".format(total_value_fiat))
        log.info("Initial total investment: {:.6f} BTC".format(total_value_btc))
        portfolio['total_value_fiat'] = total_value_fiat
        portfolio['total_value_btc'] = total_value_btc
        portfolio['total_gain_percentage'] = 0

        portfolio['last_updated'] = int(time())

        with open("data/portfolio.json", 'w') as f:
            json.dump(portfolio, f, sort_keys=True, indent=4)

        return portfolio

    def __create_trade(self, from_currency, to_currency, value):
        if self.__portfolio['crypto_currencies'][from_currency]['investment'] >= value:
            trade = {
                'value': value,
                'from_currency': from_currency,
                'to_currency': to_currency,
                'completed': False
            }
            self.__trades.append(trade)

            log.info("Created new trade for {}.".format(self.__portfolio['crypto_currencies'][from_currency]['name']))
        else:
            log.warning("Trade could not be created. Too low funding.")

    def __Trader(self):
        sleep(10)
        while True:
            log.debug("Checking for trades.")
            for trade in self.__trades:
                if trade['completed']:
                    continue
                log.info("+++++++++++++++++++++")

                from_currency_name = self.__market['crypto_currencies'][trade['from_currency']]['name']
                from_currency_symbol = self.__market['crypto_currencies'][trade['from_currency']]['symbol']
                to_currency_name = self.__market['crypto_currencies'][trade['to_currency']]['name']
                to_currency_symbol = self.__market['crypto_currencies'][trade['to_currency']]['symbol']
                trade_value_fiat = trade['value'] * self.__market['crypto_currencies'][trade['from_currency']]['price_usd']
                trade_price = self.__market['crypto_currencies'][trade['from_currency']]['price_usd'] * pow(self.__market['crypto_currencies'][trade['to_currency']]['price_usd'], -1)

                log.info("Trading {:.6f} {} ({:.2f} USD) in {} for {} @ {:.6f} {}/{}.".format(trade['value'], from_currency_symbol, trade_value_fiat, from_currency_name, to_currency_name, trade_price, to_currency_symbol, from_currency_symbol))
                from_currency_change = - trade['value']
                to_currency_change = trade['value'] * self.__market['crypto_currencies'][trade['from_currency']]['price_btc']

                from_currency_investment = self.__portfolio['crypto_currencies'][trade['from_currency']]['investment'] + from_currency_change
                from_currency_value_fiat = self.__portfolio['crypto_currencies'][trade['from_currency']]['value_fiat'] - trade_value_fiat
                to_currency_investment = self.__portfolio['crypto_currencies'][trade['to_currency']]['investment'] + to_currency_change
                to_currency_value_fiat = self.__portfolio['crypto_currencies'][trade['to_currency']]['value_fiat'] + trade_value_fiat
                trading_timestamp = int(time())
                self.__portfolio['crypto_currencies'][trade['from_currency']].update({
                    'investment': from_currency_investment,
                    'value_fiat': from_currency_value_fiat,
                    'value_fiat_at_last_trade': from_currency_value_fiat,
                    'last_change': trading_timestamp
                })
                self.__portfolio['crypto_currencies'][trade['to_currency']].update({
                    'investment': to_currency_investment,
                    'value_fiat_at_last_trade': to_currency_value_fiat,
                    'value_fiat_at_last_trade': to_currency_value_fiat,
                    'last_change': trading_timestamp
                })
                trade['completed'] = True

                log.info("Trade successful!")
                log.info("New trading pair balance: {:.6f} {} ({:.2f} USD), {:.6f} {} ({:.2f} USD).".format(from_currency_investment, from_currency_symbol, from_currency_value_fiat, to_currency_investment, to_currency_symbol, to_currency_value_fiat))
                log.info("+++++++++++++++++++++")
            sleep(3)

    def __MarketUpdater(self):
        while True:
            self.__market = request_market()
            log.debug("Market updated.")
            sleep(10)

    def __PortfolioUpdater(self):
        sleep(1)
        while True:
            self.__portfolio = self.evaluate_portfolio(self.__portfolio, self.__market)
            with open("data/portfolio.json", 'w') as f:
                json.dump(self.__portfolio, f, sort_keys=True, indent=4)

            log.debug("Portfolio updated.")
            sleep(5)

    def __Ticker(self):
        sleep(3)
        while True:
            log.info("====================")
            log.info("Portfolio Summary")
            for cc in self.__portfolio['crypto_currencies']:
                symbol = self.__portfolio['crypto_currencies'][cc]['symbol']
                value = self.__portfolio['crypto_currencies'][cc]['investment']
                value_fiat = self.__portfolio['crypto_currencies'][cc]['investment'] * self.__market['crypto_currencies'][cc]['price_usd']
                gain_percentage = self.__portfolio['crypto_currencies'][cc]['gain_percentage']
                log.info("{:.6f} {} ({:.2f} USD), {:+.2f} %".format(value, symbol, value_fiat, gain_percentage))

            total_value_fiat = self.__portfolio['total_value_fiat']
            total_value_btc = self.__portfolio['total_value_btc']
            total_gain_percentage = self.__portfolio['total_gain_percentage']
            log.info("--------------------")
            log.info("Portfolio value: {:.6f} BTC ({:.2f} USD), {:+.2f} %".format(total_value_btc, total_value_fiat, total_gain_percentage))
            log.info("====================")
            sleep(60)

    def __Run(self):
        sleep(5)
        swap_threshold_percentage = self.__config['swap_threshold_percentage']
        while True:
            log.debug("HODLbot running.")
            for cc in self.__portfolio['crypto_currencies']:
                if cc is "bitcoin":
                    continue

                name = self.__portfolio['crypto_currencies'][cc]['name']
                value_fiat = self.__portfolio['crypto_currencies'][cc]['value_fiat']
                value_fiat_at_last_trade = self.__portfolio['crypto_currencies'][cc]['value_fiat_at_last_trade']
                gain = (value_fiat / value_fiat_at_last_trade - 1)
                gain_percentage = gain * 100
                if gain_percentage > swap_threshold_percentage:
                    log.info("Found a {} gain of {:.2f} %, swapping half of it.".format(name, gain_percentage))
                    self.__create_trade(cc, "bitcoin", 0.5 * gain * self.__portfolio['crypto_currencies'][cc]['investment'])
            sleep(30)
