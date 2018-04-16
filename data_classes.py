from datetime import datetime as dt

class TimeData():
	def __init__(self):
		self.data_start_date = dt.now()
		self.data_end_date = dt.now()
		self.categories = []
		self.raw_data = []		# the initial raw CSV data read from the CSV file
		self.parsed_data = []	# the CSV data after it has been parsed to convert strings into
								# datetime objects
		self.binned_data = {}	# the final dictionary of data[date][hour][category]
								# date is a datetime object, hour is an integer, and category is a string

	def read_csv_data(self):

	def populate_categories(self):

