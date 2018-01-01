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
* Value summary
* Offline trading implementation
* Algorithm
* Simulation for proof of concept based on historic data
* Online trading via APIs
