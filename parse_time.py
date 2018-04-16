from datetime import datetime as dt
import datetime as dateandtime
import extend_time as et


def parse_line(line):

	# Sections 1 and 2 contain date data. this date data needs to be processed so we can read it.
	n = 1
	start_pm = 0
	end_pm = 0

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

	start_datetime = dt.strptime(line[1], "%x %X %p") + dateandtime.timedelta(hours=start_pm)

	end_datetime = dt.strptime(line[2], "%x %X %p") + dateandtime.timedelta(hours=end_pm)

	# apparently the datetime library is clueless about how to handle PM, so we will have to do that too.

	return [line[0], start_datetime, end_datetime]

