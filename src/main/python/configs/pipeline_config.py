from config_loader import ConfigLoader

PIPELINE_CONFIGS = ConfigLoader().load('conf/pipeline_config.yml')
STAGES_CONFIG = PIPELINE_CONFIGS['stages']
FLAGGED_ELEMENTS = PIPELINE_CONFIGS['flagged']
