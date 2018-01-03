# HODLbot
Drives the HODL strategy to an automated level across crypto currencies.

## Idea
Use the HODL strategy for accumulating wealth on a desired main crypto currency (CC). Spread your initial investment across the top 10 crypto currencies based on market capitalizations and dynamically swaps a part of the gains to your loved CC while hodl'ing onto your initial investment. Never sells your main CC.

## Installing and Running
Prerequisites: Git and Python 3

Installation:
* Clone repository with ``git clone https://github.com/HODLorg/HODLbot.git``
* Copy ``config/config.py.example``, customize configuration and save as ``config/config.py``

Running:
* Run in console with ``python start_bot.py``

## ToDo
* ~~Collect data from https://coinmarketcap.com/~~
* ~~Import/Create a portfolio~~
* ~~Value summary~~
* ~~Offline trading implementation~~
* ~~Algorithm~
* Simulation for proof of concept based on historic data
* Online trading via APIs

## Example
Running on live data for 12 hours:
```
[2018-01-03 10:55:37,259][          Ticker][   bot][    INFO] Portfolio Summary
[2018-01-03 10:55:37,260][          Ticker][   bot][    INFO] 117.884622 ADA (114.57 USD), +14.57 %
[2018-01-03 10:55:37,260][          Ticker][   bot][    INFO] 0.387291 LTC (97.53 USD), -2.47 %
[2018-01-03 10:55:37,260][          Ticker][   bot][    INFO] 83.161609 XEM (105.62 USD), +5.62 %
[2018-01-03 10:55:37,260][          Ticker][   bot][    INFO] 0.011825 BTC (179.19 USD), +79.19 %
[2018-01-03 10:55:37,260][          Ticker][   bot][    INFO] 0.083420 DASH (96.70 USD), -3.30 %
[2018-01-03 10:55:37,260][          Ticker][   bot][    INFO] 0.112354 ETH (99.19 USD), -0.81 %
[2018-01-03 10:55:37,260][          Ticker][   bot][    INFO] 38.941069 XRP (106.60 USD), +6.60 %
[2018-01-03 10:55:37,260][          Ticker][   bot][    INFO] 160.535480 XLM (123.51 USD), +23.51 %
[2018-01-03 10:55:37,260][          Ticker][   bot][    INFO] 24.673721 MIOTA (98.24 USD), -1.76 %
[2018-01-03 10:55:37,260][          Ticker][   bot][    INFO] 0.035131 BCH (97.74 USD), -2.26 %
[2018-01-03 10:55:37,261][          Ticker][   bot][    INFO] --------------------
[2018-01-03 10:55:37,261][          Ticker][   bot][    INFO] Portfolio value: 0.074598 BTC (1118.89 USD), +11.89 %
```
