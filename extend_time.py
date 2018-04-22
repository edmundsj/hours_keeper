# This extends the standard library datetime objects with "floor" and "ceiling" functions
import datetime


def time_floor(date, t="hour"):
	if t == "hour":
		return date.replace(microsecond=0, second=0, minute=0)
	elif t == "day":
		return date.replace(microsecond=0, second=0, minute=0, hour=0)
	else:
		raise LookupError("Can't find the date floor you were requesting.")


def time_ceiling(date, t="hour"):
	""" Calculates the date rounded up to the nearest hour or day

	"""
	if t == "hour":
		return date.replace(microsecond=0, second=0, minute=0) + datetime.timedelta(hours=1)
	elif t == "day":
		return date.replace(microsecond=0, second=0, minute=0, hour=0) + datetime.timedelta(days=1)
	else:
		raise LookupError("Can't find the date ceiling you were requesting.")
