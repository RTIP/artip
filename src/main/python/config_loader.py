import yaml


class ConfigLoader:
    def load(self, config_file_name):
        config_file = open(config_file_name)
        configs = yaml.load(config_file)
        config_file.close()
        return configs
