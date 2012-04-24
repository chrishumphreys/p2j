"""     
        Written By:
                Chris Humphreys
                Email: < chris (--AT--) habitualcoder [--DOT--] com >
 
        Copyright Chris Humphreys 2010
 
        This program is free software; you can redistribute it and/or modify
        it under the terms of the GNU General Public License as published by
        the Free Software Foundation; either version 3 of the License, or
        (at your option) any later version.
 
        This program is distributed in the hope that it will be useful,
        but WITHOUT ANY WARRANTY; without even the implied warranty of
        MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
        GNU General Public License for more details.
 
        You should have received a copy of the GNU General Public License
        along with this program.  If not, see <http://www.gnu.org/licenses/>.
 """


import os
import sys
import inspect
from types import *
from collections import OrderedDict # Requires Python 2.7+
import pprint
import cPickle

from gameengine import *

TRACE_BASE = "/home/chris/ab/gamemenu.py"

TRACE_FILE_EXT='.trace'
TRACE_RETURN_FILE_EXT='.return-trace'

TRACE_PICKLED_FILE_EXT='.pickled-trace'
TRACE_PICKLED_RETURN_FILE_EXT='.pickled-return-trace'


USE_RELATIVE_SOURCE_FILE_PATHS = True
DEBUG_TRACEIT = True

trace_data = dict()
trace_return_data = dict()


def describe_arg(a, arg_values):
	if type(a) is StringType:
		if a != "self":
			a_value = arg_values.locals[a]
			a_type = a_value.__class__.__name__
			return a, a_type
		else:
			return None, None
	elif type(a) is ListType: # ListType is not hashable
		return "anonymous_list", str(a)
	else:
		print "Unexpected type for %s: %s" % (a, type(a))
		return None, None


def traceit(frame, event, arg):

	#http://docs.python.org/library/sys.html#sys.settrace
	#http://docs.python.org/library/inspect.html
	if event == "call" or event == "return":
		filename = frame.f_code.co_filename
		if filename[0:len(TRACE_BASE)] == TRACE_BASE:

			frame_info = inspect.getframeinfo(frame)
			file_path = frame_info.filename
			if USE_RELATIVE_SOURCE_FILE_PATHS:
				dir, file_name = os.path.split(file_path)
			else:
				file_name = file_path

			key = file_name + ":" + str(frame_info.lineno) + ":" + frame_info.function

			if event == "call":
				if key in trace_data:
					this_trace = trace_data[key]
				else:
					this_trace = OrderedDict()
					trace_data[key] = this_trace

				arg_values = inspect.getargvalues(frame)
				for a in arg_values.args:
					arg_name, type = describe_arg(a, arg_values)
					if arg_name is not None:
						if arg_name in this_trace:
							types_set = this_trace[arg_name]
							if type not in types_set:
								types_set.add(type)
						else:
							types_set = set()
							types_set.add(type)
							this_trace[arg_name] = types_set

				#if DEBUG_TRACEIT:
				#	print key + args
			elif event == "return":
				if key in trace_return_data:
					types_set = trace_return_data[key]
				else:
					types_set = set()
					trace_return_data[key] = types_set

				if arg is None:
					type = "void"
				else:
					type = arg.__class__.__name__

				types_set.add(type)


	return traceit

def description_for_types_set(types_set):
	return "/".join(types_set)

def description_for_arg_values(arg_values):
	description = ""
	for arg_name, types_set in arg_values.iteritems():
		description += ":" + arg_name
		if len(types_set) > 0:
			description += "," + description_for_types_set(types_set)
	return description


def compare_keys(item1, item2):
	parts1 = item1[0].split(":")
	parts2 = item2[0].split(":")

	filename1 = parts1[0]
	filename2 = parts2[0]

	filename_cmp = cmp(filename1, filename2)
	if filename_cmp == 0:
		line1 = int(parts1[1])
		line2 = int(parts2[1])

		line_cmp = cmp(line1, line2)
		if line_cmp == 0:
			method1 = parts1[2]
			method2 = parts2[2]

			method_cmp = cmp(method1, method2)
			return method_cmp
		else:
			return line_cmp
	else:
		return filename_cmp


def save_trace(trace_dict, extension):
	current_dir = os.getcwd() + "/"
	prev_file = None
	output = None

	for key, value in iter(sorted(trace_dict.items(), cmp=compare_keys)):
		current_file, tail = key.split(":", 1)

		if current_file != prev_file:
			if output is not None:
				output.close()

			if USE_RELATIVE_SOURCE_FILE_PATHS:
				current_file_path = current_dir + current_file
			else:
				current_file_path = current_file

			output = open(current_file_path + extension, "w")

			prev_file = current_file

		if isinstance(value, OrderedDict):
			value_string = description_for_arg_values(value)
		elif isinstance(value, set):
			value_string = ":" + description_for_types_set(value)

		pair_string = key + value_string + "\n"
		output.write(pair_string)

	if output is not None:
		output.close()

def pickle_data(trace_dict, pickle_file_path):
	try:
		pickle_file = open(pickle_file_path, 'wb')
	except IOError as e:
		print "Couldn't write pickled data to " + pickle_file_path
		return

	cPickle.dump(trace_dict, pickle_file)

	pickle_file.close()

def unpickle_data(pickle_file_path):
	try:
		pickle_file = open(pickle_file_path, 'rb')
	except IOError as e:
		print "No previous pickled data at " + pickle_file_path
		return dict()

	trace_data = cPickle.load(pickle_file)

	pickle_file.close()

	return trace_data

if __name__ == '__main__':
	print "starting"
	sys.settrace(traceit)

	targeted_file_path = sys.argv[1]

	trace_data = unpickle_data(targeted_file_path + TRACE_PICKLED_FILE_EXT)
	trace_return_data = unpickle_data(targeted_file_path + TRACE_PICKLED_RETURN_FILE_EXT)

	main(sys.argv[1:])

	#pp = pprint.PrettyPrinter(indent=4)
	#pp.pprint(trace_data)

	save_trace(trace_data, TRACE_FILE_EXT)
	save_trace(trace_return_data, TRACE_RETURN_FILE_EXT)

	pickle_data(trace_data, targeted_file_path + TRACE_PICKLED_FILE_EXT)
	pickle_data(trace_return_data, targeted_file_path + TRACE_PICKLED_RETURN_FILE_EXT)

