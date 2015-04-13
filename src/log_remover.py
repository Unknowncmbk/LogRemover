''' 
Project overview:
	Write a shell script (in your favorite scripting language for Windows or Linux) 
	that can be run daily to search a directory tree and remove all the oldest .log
	files to bring the total filesystem utilization down to 80%.

	Questions to ask Raffi:
	- Do you want the oldest log files based on creation or modified date?

	References:
	- Finding file by pattern: http://stackoverflow.com/questions/1724693/find-a-file-in-python
	- Sorting: https://docs.python.org/2/howto/sorting.html#sortinghowto
	- Calculating disk usage: https://docs.python.org/2/library/statvfs.html
	- Logging: https://docs.python.org/2.6/library/logging.html

	Issues ran into:
	- When computing _get_disk_usage(), used space is calculated as total blocks - free blocks * block size. 
		The issue with this is a file is shown in the filesystem as bytes. A 512 byte file is 1/2 a block.
		Therefore in _remove_files(), we should be calculating the number of blocks that we are removing 
		from used, and not just the size of the file.

	Total hours: 2.5 - 3 hours, ~15 mins for planning, ~1 hour testing.

'''

#!/usr/bin/env python
import sys, os, fnmatch, time
# used for logging
import glob, logging, logging.handlers

# What utilization do we want to keep the filesystem under
TOTAL_UTILIZATION = 0.8
# File that the results of this script writes to
LOG_FILENAME = 'log_remover.log'
# construct logger
LOG = logging.getLogger('log_remover')
LOG.setLevel(logging.DEBUG)
handler = logging.handlers.RotatingFileHandler(LOG_FILENAME, backupCount=5)
LOG.addHandler(handler)

def _get_disk_usage(path):
	"""
	Args:
		path: full /path/to/dir/ to get utilization of

	Returns:
		A tuple consisting of the total space, the 
		used space, the free space, and the percent utilization.
	"""
	stat = os.statvfs(path)

	free = stat.f_bfree * stat.f_frsize
	total = stat.f_blocks * stat.f_frsize
	used = (stat.f_blocks - stat.f_bfree) * stat.f_frsize

	try:
		percent = (float(used) / total) * 100
	except ZeroDivisionError:
		percent = 0

	return total, used, free, round(percent, 1)

def _remove_files(files, disk_usage):
	"""
	Args:
		files: files that can be deleted
		disk_usage: the disk_usage details, including total space, and used space

	Returns:
		A list of all /path/to/files that were removed and the new used space.
	"""

	total = disk_usage[0]
	used = disk_usage[1]
	goal = TOTAL_UTILIZATION * total

	# size of 1 block in bytes
	block_size = os.statvfs(path).f_frsize

	# list of files we removed
	removed = []

	while used > goal:

		# if there are files left
		if len(files) > 0:
			# get head file tuple (path, size, timestamp)
			f_tup = files.pop(0)
			f_name = f_tup[0]
			f_size = (f_tup[1] // block_size) + 1

			# mark file to be removed and remove it
			removed.append(f_name)
			os.remove(f_tup[0])

			# calculate used now
			used -= f_size * block_size
		else:
			break

	return removed, used

def _find_files(path, pattern):
	"""
	Args:
		path: full /path/to/dir/ to explore
		pattern: pattern that we want to match in a file name

	Returns:
		A list of tuples where the first element is the name of the file, 
		the second element is the size of the file, and the third element
		is the last modified timestamp of the file.

	"""
	result = []

	for root, dirs, files in os.walk(path):
		for name in files:
			if fnmatch.fnmatch(name, pattern):

				# full path to file reference from this path
				abs_file = os.path.join(root, name)
				# size of the file
				size = os.path.getsize(abs_file)
				# timestamp of the file
				stamp = time.ctime(os.path.getmtime(abs_file))

				result.append((abs_file, size, stamp))

	return result

# Execute from command line
if len(sys.argv) > 1:
	path = sys.argv[1]
	disk_usage = _get_disk_usage(path)

	# If we want to run the rest of the script
	if disk_usage[3] > TOTAL_UTILIZATION * 100:

		LOG.debug(str(time.ctime(time.time())) + ": Disk usage of " + str(disk_usage[3]) + "% exceeds limit of " + str(TOTAL_UTILIZATION * 100) + "%.")

		# find all .log files in path
		files = _find_files(path, '*.log')

		# sort files based on modified date
		files = sorted(files, key=lambda date: date[2])

		# used is for debugging purposes, used == disk_usage[3]
		removed, used = _remove_files(files, disk_usage)

		for r in removed:
			LOG.debug(str(time.ctime(time.time())) + ": Removed " + str(r))

		# log the results of this script
		disk_usage = _get_disk_usage(path)
		if disk_usage[3] < TOTAL_UTILIZATION * 100:
			LOG.debug(str(time.ctime(time.time())) + ": Usage of " + str(disk_usage[3]) + "% within limit of " + str(TOTAL_UTILIZATION * 100) + "%.")
		else:
			LOG.debug(str(time.ctime(time.time())) + ": Removed all .log files within " + str(path) + ", however, usage is still at " + str(disk_usage[3]) + "%.")
