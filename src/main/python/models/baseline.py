class Baseline:
	def __init__(self, antenna1,antenna2, polarization, scan_id):
		self.antenna1 = int(antenna1)
		self.antenna2 = int(antenna2)
		self.polarization = polarization
		self.scan_id = scan_id

	def __repr__(self):
		return str(self.polarization) + "-" + str(self.scan_id) + ": "+ str(self.antenna1) + "-" + str(self.antenna2)

	def __eq__(self, other):
		return other.__dict__ == self.__dict__