from config_loader import ConfigLoader
import platform

ALL_CONFIGS = ConfigLoader().load('conf/config.yml')
GLOBAL_CONFIG = ALL_CONFIGS['global']
DETAIL_FLAG_CONFIG = ALL_CONFIGS['flux_calibration']['detail_flagging']
DATASET_PATH = None
FLAG_FILE = None
CASAPY_CONFIG = ALL_CONFIGS['casapy'][platform.system()]
