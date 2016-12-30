from config_loader import ConfigLoader

ALL_CONFIGS = ConfigLoader().load('conf/config.yml')
GLOBAL_CONFIG = ALL_CONFIGS['global']
FLUX_CAL_CONFIG = ALL_CONFIGS['flux_calibration']
DETAIL_FLAG_CONFIG = FLUX_CAL_CONFIG['detail_falgging']
DATASET = None
CASAPY_CONFIG = ALL_CONFIGS['casapy']
