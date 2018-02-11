import os
import coloredlogs
import config


def load():
    # default log format
    # %(asctime)s %(hostname)s %(name)s[%(process)d] %(levelname)s %(message)s
    formatter = "[%(funcName)s] %(levelname)s %(message)s"
    os.environ['COLOREDLOGS_LOG_FORMAT'] = formatter
    coloredlogs.install(level=config.PIPELINE_CONFIGS['log_level'])