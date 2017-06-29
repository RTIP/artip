from config_loader import ConfigLoader

PIPELINE_CONFIGS = None
STAGES_TOGGLE_CONFIG = None

def load(config_path):
    global PIPELINE_CONFIGS, STAGES_TOGGLE_CONFIG

    PIPELINE_CONFIGS = ConfigLoader().load(config_path)
    STAGES_TOGGLE_CONFIG = PIPELINE_CONFIGS['stages']
