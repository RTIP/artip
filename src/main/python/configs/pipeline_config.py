from config_loader import ConfigLoader

PIPELINE_CONFIGS = None
STAGES_TOGGLE_CONFIG = None
FLAGGED_ELEMENTS = None

def load(config_path):
    global PIPELINE_CONFIGS, STAGES_TOGGLE_CONFIG, FLAGGED_ELEMENTS

    PIPELINE_CONFIGS = ConfigLoader().load(config_path)
    STAGES_TOGGLE_CONFIG = PIPELINE_CONFIGS['stages']
    FLAGGED_ELEMENTS = PIPELINE_CONFIGS['flagged']
