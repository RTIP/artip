import yaml

class Config:
	def __init__(self,config_file):
		config = open(config_file)
		self.__properties = yaml.load(config)
		config.close()

	def global_configs(self):
		return self.__properties['global']

	def flux_cal_configs(self):
		return self.__properties['flux_calibration']