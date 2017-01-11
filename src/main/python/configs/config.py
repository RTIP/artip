from config_loader import ConfigLoader

ALL_CONFIGS = ConfigLoader().load('conf/config.yml')
GLOBAL_CONFIG = ALL_CONFIGS['global']
DETAIL_FLAG_CONFIG = ALL_CONFIGS['flux_calibration']['detail_falgging']
DATASET = None
CASAPY_CONFIG = ALL_CONFIGS['casapy']
