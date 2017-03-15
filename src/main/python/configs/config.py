from config_loader import ConfigLoader
import platform

ALL_CONFIGS = ConfigLoader().load('conf/config.yml')
GLOBAL_CONFIG = ALL_CONFIGS['global']
OUTPUT_PATH = GLOBAL_CONFIG['output_path']
CASAPY_CONFIG = ALL_CONFIGS['casapy'][platform.system()]
