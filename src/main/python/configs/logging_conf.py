import os
import logging
import coloredlogs
from debugging_config import DEBUG_CONFIGS


def logging_config():
    # default log format
    # %(asctime)s %(hostname)s %(name)s[%(process)d] %(levelname)s %(message)s
    formatter = "[%(funcName)s] %(levelname)s %(message)s"
    os.environ['COLOREDLOGS_LOG_FORMAT'] = formatter
    coloredlogs.install(level=DEBUG_CONFIGS['log_level'])