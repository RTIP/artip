from config_loader import ConfigLoader

DEBUG_CONFIGS = ConfigLoader().load('conf/debug_config.yml')
DEBUG_FLAG_ELEMENTS = DEBUG_CONFIGS['flagged']
