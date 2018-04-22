from datetime import datetime as dt
import datetime as datetime
import csv
from extend_time import *
import numpy as np

# TODO: IF DATA IS NOT SORTED BY DATE, THEN SORT IT BY DATE.


class TimeData():
	def __init__(self, filename):
		# Setup all data objects
		self.data_start_date = dt.now()		# the start date of the data
		self.data_end_date = dt.now()		# the end date of the data
		self.categories = []		# the array containing the activity categories defined by the .csv file
		self.raw_data = []			# the initial raw CSV data read from the CSV file
		self.parsed_data = []		# the CSV data after it has been parsed to convert strings to datetime
		self.binned_data = {}		# the final dictionary of data[date][hour][category]

		self.setup(filename)		# contains subroutines to read data, parse data, and populate data structures

	'''
	@filename the name of the HoursKeeper CSV file
	'''
	def setup(self, filename):
		self.read_csv_data(filename)

		# parses csv data to create dates and times out of strings, discards unnecessary information
		self.parse_csv_data()

		# populates the categories intelligently based on all the data
		self.populate_categories()

		# sets up our binned data object to contain the appropriate number of empty dictionaries with
		# the correct structure
		self.setup_binned_data()

		# populates the binned data object based on the parsed csv data
		self.populate_binned_data()

	def read_csv_data(self, filename):
		with open(filename) as f:
			csv_data = csv.reader(f)

			for line in csv_data:
				self.raw_data.append(line)

	'''
	Parses CSV data from raw_data
	'''
	def parse_csv_data(self):
		i = 0

		for line in self.raw_data:
			if i != 0:
				self.parsed_data.append(self.parse_data_line(line))
			i += 1

	'''
	Populates the internal categories array from parsed_data
	'''
	def populate_categories(self):
		for line in self.parsed_data:
			if line[0] not in self.categories:
				self.categories.append(line[0])

	'''
	At this point, we have a collection of tasks in order from oldest to most recent, located in
	parsed_data. parsed_data[0] represents the oldest event. Now we just need to add data to bins
	as appropriate. Let's set up our bins based on the first and the last date.
	'''
	def setup_binned_data(self):
		self.data_start_date = time_floor(self.parsed_data[0][1], "day")
		final_index = len(self.parsed_data) - 1
		self.data_end_date = time_floor(self.parsed_data[final_index][1], "day")
		num_days = (self.data_end_date - self.data_start_date).days

		# Now we proceed to create the bins dictionary, and we can fill it as needed.
		i = 0
		while i <= num_days:
			current_date = self.data_start_date + datetime.timedelta(days=i)
			self.binned_data[current_date] = {}		# create an empty dictionary that contains the hours

			# Populate the hours within the inner dictionary
			h = 0
			while h <= 23:
				self.binned_data[current_date][h] = {}  # create our innermost dictionary that contains the tasks

				c = 0
				while c < len(self.categories):
					self.binned_data[current_date][h][self.categories[c]] = 0
					c += 1
				h += 1
			i += 1

	def populate_binned_data(self):
		index_counter = 0

		for line in self.parsed_data:
			task_start_time = line[1]
			task_end_time = line[2]
			task_category = line[0]

			# crawl through the hours, adding time to our bins as necessary.
			time_delta = task_end_time - task_start_time
			current_time = task_start_time
			current_day = time_floor(current_time, "day")

			is_first_hour = True

			while time_delta.seconds > 0 and time_delta.days >= 0:

				# this only needs to be executed the first time to check if we have a task less than 1 hour in duration
				if is_first_hour:
					is_first_hour = False
					# this is the case when our task is entirely within-hour in the same day
					if time_floor(task_start_time) == time_floor(task_end_time):
						self.binned_data[current_day][current_time.hour][task_category] = \
							(task_end_time - current_time).seconds / 3600
						break

					# otherwise, just floor the time to the nearest hour (it will be incremented below)
					# and set the bin time appropriately
					else:
						next_hour = time_ceiling(current_time)
						num_seconds = (next_hour - current_time).seconds
						num_hours = num_seconds / 3600

						self.binned_data[current_day][current_time.hour][task_category] = num_hours
						current_time = time_floor(current_time)

				else:
					# if our time delta is greater than 3600, then the entire hour is taken up
					if time_delta.seconds > 3600 or time_delta.days > 0:
						self.binned_data[current_day][current_time.hour][task_category] = 1
					# if our time delta is less than 1 hour, that means only part of the hour is taken up, and we are done.
					else:
						self.binned_data[time_floor(current_time, "day")][current_time.hour][task_category] = \
							(task_end_time - current_time).seconds / 3600
						break

				current_time = current_time + datetime.timedelta(hours=1)
				current_day = time_floor(current_time, "day")
				time_delta = task_end_time - current_time
			index_counter += 1

	def generate_hourly_data(self, start_date, end_date):
		num_days = (end_date - start_date).days
		plot_data = []		# a set of data for each activity in each hour of the day

		i = 0		# an iterator
		for c in self.categories:		# loop through each category
			plot_data.append([])
			for n in range(24):		# loop through each hour in each category
				plot_data[i].append(0.0)

				current_date = start_date
				while current_date != end_date:		# loop through each date and add data
					plot_data[i][n] += self.binned_data[current_date][n][c]
					current_date += datetime.timedelta(days=1)

				# now normalize the data by the number of days
				plot_data[i][n] /= num_days

			i += 1
		return plot_data
# Now we loop through all the individual tasks in data and add to the 'bins' section

	@staticmethod
	def parse_data_line(line):

		# Sections 1 and 2 contain date data. this date data needs to be processed so we can read it.
		n = 1
		start_pm = 0			# variable to let us deal with AM/PM manually
		end_pm = 0
		category = line[0]

		while n <= 2:

			# change the date section time to include
			line[n] = line[n][0:-3] + ":00" + line[n][-3:] # reassemble it

			# correct for the fact that 12AM is actually 00:00
			if line[n][-2:] == "AM" and line[n][-11:-9] == "12":
				if n == 1:
					start_pm = -12
				else:
					end_pm = -12
			# correct for the fact that 1PM is actually 13:00 and so on, but 12pm is actually 12:00
			if line[n][-2:] == "PM" and line[n][-11:-9] != "12":
				if n == 1:
					start_pm = 12
				else:
					end_pm = 12

			if line[n][1] == "/":  # The month is a single digit. We need to add a zero out front.
				line[n] = "0" + line[n]

			n += 1

		start_datetime = dt.strptime(line[1], "%x %X %p") + datetime.timedelta(hours=start_pm)

		end_datetime = dt.strptime(line[2], "%x %X %p") + datetime.timedelta(hours=end_pm)

		# apparently the datetime library is clueless about how to handle PM, so we will have to do that too.

		return [category, start_datetime, end_datetime]
