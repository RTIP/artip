import yaml


class Config:
    def __init__(self, config_file):
        config = open(config_file)
        self.__properties = yaml.load(config)
        config.close()

    def global_configs(self):
        return self.get('global')

    def get(self, _for):
        return self.__properties[_for]
