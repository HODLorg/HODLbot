#!/usr/bin/python

import sys
import logging

from time import sleep

from config.config import config
from hodlbot.bot import HODLbot

log_level = "INFO" #if config['debug'] else "INFO"
logging.basicConfig(level=log_level, format="[%(asctime)s][%(threadName)16s][%(module)6s][%(levelname)8s] %(message)s")
logging.getLogger("requests").setLevel(logging.WARNING)
log = logging.getLogger()

bot = HODLbot(config)
bot.start()

# Keep the main thread alive.
while True:
    sleep(1)
