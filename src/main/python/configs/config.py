from config_loader import ConfigLoader

ALL_CONFIGS = None
GLOBAL_CONFIG = None
OUTPUT_PATH = None
CASA_CONFIG = None

def load(config_path):
    global ALL_CONFIGS, GLOBAL_CONFIG, OUTPUT_PATH, CASA_CONFIG
    ALL_CONFIGS = ConfigLoader().load(config_path + "config.yml")
    GLOBAL_CONFIG = ALL_CONFIGS['global']
    OUTPUT_PATH = GLOBAL_CONFIG['output_path']
    CASA_CONFIG = ConfigLoader().load(config_path + "casa.yml")
