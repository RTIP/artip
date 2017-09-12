from config_loader import ConfigLoader

ALL_CONFIGS = None
PIPELINE_CONFIGS = None
STAGE_CONFIGS = None
TARGET_SOURCE_CONFIGS = None
GLOBAL_CONFIGS = None
CONFIG_PATH = None
OUTPUT_PATH = None
CASA_CONFIGS = None

def load(config_path):
    global ALL_CONFIGS, TARGET_SOURCE_CONFIGS, STAGE_CONFIGS, PIPELINE_CONFIGS, GLOBAL_CONFIGS, CONFIG_PATH, OUTPUT_PATH, CASA_CONFIGS
    ALL_CONFIGS = ConfigLoader().load(config_path + "config.yml")
    PIPELINE_CONFIGS = ConfigLoader().load(config_path + "pipeline.yml")
    TARGET_SOURCE_CONFIGS = ConfigLoader().load(config_path + "target_source.yml")
    CASA_CONFIGS = ConfigLoader().load(config_path + "casa.yml")

    GLOBAL_CONFIGS = PIPELINE_CONFIGS['global']
    STAGE_CONFIGS = PIPELINE_CONFIGS['stages']
    CONFIG_PATH = config_path
    OUTPUT_PATH = GLOBAL_CONFIGS['output_path']
