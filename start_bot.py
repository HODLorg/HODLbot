#!/usr/bin/python

import sys
import logging

from time import sleep

from config.config import config
from hodlbot.bot import HODLbot

log_level = "DEBUG" #if config['debug'] else "INFO"
logging.basicConfig(level=log_level, format="[%(asctime)s][%(threadName)13s][%(module)3s][%(levelname)8s] %(message)s")
logging.getLogger("requests").setLevel(logging.WARNING)
log = logging.getLogger()

bot = HODLbot(config)
bot.start()

# Keep the main thread alive.
while True:
    sleep(1)
