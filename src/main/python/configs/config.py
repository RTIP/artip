from config_loader import ConfigLoader
import platform

ALL_CONFIGS = None
GLOBAL_CONFIG = None
OUTPUT_PATH = None
CASAPY_CONFIG = None

def load(config_path):
    global ALL_CONFIGS, GLOBAL_CONFIG, CASAPY_CONFIG, OUTPUT_PATH

    ALL_CONFIGS= ConfigLoader().load(config_path)
    GLOBAL_CONFIG= ALL_CONFIGS['global']
    OUTPUT_PATH= GLOBAL_CONFIG['output_path']
    CASAPY_CONFIG= ALL_CONFIGS['casapy'][platform.system()]