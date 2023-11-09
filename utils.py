
class Data:
	def __init__(self):
		self.results_lists = []
		self.filter_runs = {}
		self.smoothing_factor = 1
		self.membrane_area = 1
		self.headers = []

	def set_results(self, results_lists):
		self.results_lists = results_lists
		return self.results_lists

	def set_filter_runs(self, filter_runs):
		self.filter_runs = filter_runs
		return self.filter_runs

	def set_smoothing_factor(self, smoothing_factor):
		self.smoothing_factor = smoothing_factor
		return self.smoothing_factor

	def set_membrane_area(self, membrane_area):
		self.membrane_area = membrane_area
		return self.membrane_area

	def get_results_lists(self):
		return self.results_lists

	def get_filter_runs(self):
		return self.filter_runs

	def get_smoothing_factor(self):
		return self.smoothing_factor

	def get_membrane_area(self):
		return self.membrane_area