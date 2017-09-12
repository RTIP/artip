from config_loader import ConfigLoader

CALIBRATION_STAGES = None
CALIBRATION_CONFIGS = None
PIPELINE_CONFIGS = None
MAIN_STAGES = None
TARGET_SOURCE_STAGES = None
TARGET_SOURCE_CONFIGS = None
GLOBAL_CONFIGS = None
CONFIG_PATH = None
OUTPUT_PATH = None
CASA_CONFIGS = None


def load(config_path):
    global CALIBRATION_STAGES, CALIBRATION_CONFIGS, TARGET_SOURCE_STAGES, \
        TARGET_SOURCE_CONFIGS, MAIN_STAGES, PIPELINE_CONFIGS, \
        GLOBAL_CONFIGS, CONFIG_PATH, OUTPUT_PATH, CASA_CONFIGS

    CALIBRATION_STAGES = ConfigLoader().load(config_path + "calibration.yml")['calibration_stages']
    CALIBRATION_CONFIGS = ConfigLoader().load(config_path + "calibration.yml")['calibration']
    PIPELINE_CONFIGS = ConfigLoader().load(config_path + "pipeline.yml")
    TARGET_SOURCE_STAGES = ConfigLoader().load(config_path + "target_source.yml")['target_source_stages']
    TARGET_SOURCE_CONFIGS = ConfigLoader().load(config_path + "target_source.yml")['target_source']
    CASA_CONFIGS = ConfigLoader().load(config_path + "casa.yml")

    GLOBAL_CONFIGS = PIPELINE_CONFIGS['global']
    MAIN_STAGES = PIPELINE_CONFIGS['stages']
    CONFIG_PATH = config_path
    OUTPUT_PATH = GLOBAL_CONFIGS['output_path']
