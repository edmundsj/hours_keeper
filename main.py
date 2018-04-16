'''
This code parses data from an HoursKeeper .CSV file, and then bins the resultant data, sorted by day and hour and
category of activity into a very large dictionary. Next, the goal is to visualize that data using plots and perhaps
a user interface.

TODO: IF IT'S NOT SORTED BY DATE ALREADY, THEN SORT IT AFTER YOU PARSE IT.
'''


import csv
import parse_time
from extend_time import *
import numpy as np
import matplotlib.pyplot as plt

'''
HIGH-LEVEL PURPOSE OF THIS APPLICATION
The goal of this application is to analyze and visualize data imported from HoursKeeper,
using a basic user interface and various plotting and statistics functionality. The data is 
stored in the variable bins, which contains
'''
categories = []			# stores the high-level categories i.e. "Education / Reading / Class"
data = []				# stores all the raw CSV data. data[0] is day 0, data[1] is day 1, etc.
bins = {}				# stores our final data
num_categories = 0		# the total number of categories

# read the raw CSV data files line-by-line into the variable 'data', and parse it
# appropriately
with open("time_some_data.csv") as f:
	parsed_data = []		# stores the parsed CSV data that is date-time readable and only contains what we want.
	my_lines = []
	csv_data = csv.reader(f)

	i = 0
	for line in csv_data:
		data.append(line)
		parsed_data.append(parse_time.parse_line(data[i]))
		i += 1
	del parsed_data[0]		# delete the header line so our parser can do its magic
	data = parsed_data
	del parsed_data


# populate our categories array by searching through all our tasks
for line in data:
	if line[0] not in categories:
		categories.append(line[0])

num_categories = len(categories)
'''
At this point, we have a collection of tasks in order from oldest to most recent, located in
parsed_data. parsed_data[0] represents the oldest event. Now we just need to add data to bins 
as appropriate. Let's set up our bins based on the first and the last date.
'''
first_date = time_floor(data[0][1], "day")
final_index = len(data) - 1
last_date = time_floor(data[final_index][1], "day")
num_days = (last_date - first_date).days

# Now we proceed to create the bins dictionary, and we can fill it as needed.
i = 0
while i <= num_days:
	current_date = first_date + datetime.timedelta(days=i)
	bins[current_date] = {}		# create an empty dictionary that contains the hours

	# Populate the hours within the inner dictionary
	h = 0
	while h <= 23:
		bins[current_date][h] = {}  # create our innermost dictionary that contains the tasks

		c = 0
		while c < num_categories:
			bins[current_date][h][categories[c]] = 0
			c += 1
		h += 1
	i += 1

# Now we loop through all the individual tasks in data and add to the 'bins' section

index_counter = 0;

for line in data:
	task_start_day = time_floor(line[1], "day")
	task_end_day = time_floor(line[2], "day")
	task_start_time = line[1]
	task_end_time = line[2]
	task_category = line[0]

	# crawl through the hours, adding time to our bins as necessary.
	time_delta = task_end_time - task_start_time
	current_time = task_start_time
	current_day = time_floor(current_time, "day")

	first_hour = True

	while time_delta.seconds > 0 and time_delta.days >= 0:

		# this only needs to be executed the first time to check if we have a task less than 1 hour in duration
		if first_hour:
			first_hour = False
			# this is the case when our task is entirely within-hour in the same day
			if time_floor(task_start_time) == time_floor(task_end_time):
				bins[current_day][current_time.hour][task_category] = \
					(task_end_time - current_time).seconds / 3600
				break

			# otherwise, just floor the time to the nearest hour (it will be incremented below)
			# and set the bin time appropriately
			else:
				next_hour = time_ceiling(current_time)
				num_seconds = (next_hour - current_time).seconds
				num_hours = num_seconds / 3600

				bins[current_day][current_time.hour][task_category] = num_hours
				current_time = time_floor(current_time)

		else:
			# if our time delta is greater than 3600, then the entire hour is taken up
			if time_delta.seconds > 3600 or time_delta.days > 0:
				bins[current_day][current_time.hour][task_category] = 1
			# if our time delta is less than 1 hour, that means only part of the hour is taken up, and we are done.
			else:
				bins[time_floor(current_time, "day")][current_time.hour][task_category] = \
					(task_end_time - current_time).seconds / 3600
				break

		current_time = current_time + datetime.timedelta(hours=1)
		current_day = time_floor(current_time, "day")
		time_delta = task_end_time - current_time
	index_counter += 1


# now we try and generate a plot using matplotlib and numpy.
N = 24
ind = np.arange(N)    # the x locations for the groups
width = 0.35       # the width of the bars: can also be len(x) sequence

# TODO: CREATE A BASIC UI THAT LETS YOU TWEAK THE DATES AND SCROLL BETWEEN THEM
start_date = datetime.datetime(2018, 4, 1, 0, 0)
end_date = datetime.datetime(2018, 4, 9, 0, 0)
num_days = (end_date - start_date).days
plot_data = {}		# a set of data for each activity in each hour of the day
cumulative_data = []
ccumulative = []
for n in range(24):
	cumulative_data.append(0.0)
i = 0		# an iterator
p = []		# the plots for each of our categories
for c in categories:		# loop through each category
	plot_data[c] = []
	for n in range(24):		# loop through each hour in each category
		plot_data[c].append(0.0)

		current_date = start_date
		while current_date != end_date:		# loop through each date and add data
			plot_data[c][n] += bins[current_date][n][c]
			current_date += datetime.timedelta(days=1)

		# now normalize the data by the number of days
		plot_data[c][n] /= num_days

		cumulative_data[n] += plot_data[c][n]

	cumulative_data_copy = cumulative_data[:]
	ccumulative.append(cumulative_data_copy)

	# We want to add the *previous* cumulative data, because we want our first dataset
	# to start at zero.
	if i == 0:
		dat = np.zeros(24)
	else:
		dat = ccumulative[i - 1]
	p.append(plt.bar(ind, plot_data[c], width, bottom=dat))

	i += 1

# Now the plot data is a list of empty arrays

plt.ylabel('% of hour')
plt.title('Time Spent by Category and Hour')
plt.xticks(ind, np.arange(24))
plt.yticks(np.arange(0, 1.01, 0.1))

legend_list = []
i = 0
for item in categories:
	legend_list.append(p[i][0])
	i += 1
plt.legend(legend_list, categories)

plt.show()

print(first_date)
print(last_date)

# Before anything else, we need to parse our data so that it is readable by the datetime module.
# Basically, this just involves adding a :00 to the time of each row and adding a 0 before each
# month, if the month is only one digit long


