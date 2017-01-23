import os
import logging
import coloredlogs
from pipeline_config import PIPELINE_CONFIGS


def logging_config():
    # default log format
    # %(asctime)s %(hostname)s %(name)s[%(process)d] %(levelname)s %(message)s
    formatter = "[%(funcName)s] %(levelname)s %(message)s"
    os.environ['COLOREDLOGS_LOG_FORMAT'] = formatter
    coloredlogs.install(level=PIPELINE_CONFIGS['log_level'])