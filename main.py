'''
This code parses data from an HoursKeeper .CSV file, and then bins the resultant data, sorted by day and hour and
category of activity into a very large dictionary. Next, the goal is to visualize that data using plots and perhaps
a user interface.

TODO: IF IT'S NOT SORTED BY DATE ALREADY, THEN SORT IT AFTER YOU PARSE IT.
'''

from data_classes import *
from extend_time import *
import numpy as np
import matplotlib.pyplot as plt

'''
FUNCTION DESCRIPTION
By creating a TimeData object with a CSV filename as its argument, the TimeData class will automatically generate
necessary data structures. After the object is created the data is immediately available for use.

For plotting, the user needs to worry about a couple of functions. The first is generate_plot_data(start_date, end_date)
This extracts data from the binned_data object, starting at the start_date and ending at the end_date, which should
both be datetime.datetime objects, and should be within the range that the data exists for (otherwise it won't be 
a very interesting plot!).

HIGH-LEVEL PURPOSE OF THIS APPLICATION

The goal of this application is to analyze and visualize data imported from HoursKeeper,
using a basic user interface and various plotting and statistics functionality. The data is 
stored in the variable binned_data in the TimeData object, which contains data spent by hour. 
binned_data is a depth - 3 dictionary, with the outermost dictionary having keys of datetime.datetime objects,
the next inner dictionary having keys of integers (for the hours), and the innermost dictionary having
keys of strings which are the individual categories.


binned_data = {
	date_key:
		{ hour_key:
			{ 
				category_key: time amount
			}
		}
	}
}
as an example,

binned_data = {
	04/06/18:
		{ 
			0: {
				'Education': 0.5,
				'Deep Work': 0.4,
				'Shallow Work': 0.0
				}
			1: {
				'Education': 0.0
				'Deep Work': 1.0
				'Shallow Work': 0.0
				}
			... and so on with hours 2 through 23
		}
	... and so on with other dates
'''

# this is our TimeData object that contains all of our desired data.
data = TimeData("time_data_all.csv")


# now we try and generate a plot using matplotlib and numpy.
N = 24
ind = np.arange(N)    # the x locations for the groups
width = 0.9       # the width of the bars: can also be len(x) sequence

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
for c in data.categories:		# loop through each category
	plot_data[c] = []
	for n in range(24):		# loop through each hour in each category
		plot_data[c].append(0.0)

		current_date = start_date
		while current_date != end_date:		# loop through each date and add data
			plot_data[c][n] += data.binned_data[current_date][n][c]
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
for item in data.categories:
	legend_list.append(p[i][0])
	i += 1
plt.legend(legend_list, data.categories)

plt.show()


# Before anything else, we need to parse our data so that it is readable by the datetime module.
# Basically, this just involves adding a :00 to the time of each row and adding a 0 before each
# month, if the month is only one digit long


