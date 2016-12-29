import os
import logging
import coloredlogs

def logging_config():
    formatter = "[%(asctime)s %(funcName)s] %(message)s"
    os.environ['COLOREDLOGS_LOG_FORMAT'] = formatter
    coloredlogs.install(level=logging.INFO)