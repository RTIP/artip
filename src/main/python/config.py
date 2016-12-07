from config_loader import ConfigLoader

ALL_CONFIGS = ConfigLoader().load('conf/config.yml')
GLOBAL_CONFIG = ALL_CONFIGS['global']
FLUX_CAL_CONFIG = ALL_CONFIGS['flux_calibration']
