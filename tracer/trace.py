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
from gameengine import *

TRACE_BASE = "/home/chris/ab/gamemenu.py"

TRACE_FILE_EXT='.trace'
TRACE_RETURN_FILE_EXT='.return-trace'

OMIT_PATH = True

trace_data = dict()
trace_return_data = dict()


def describe_arg(a, arg_values):
	if type(a) is StringType:
		if a != "self":
			a_value = arg_values.locals[a]
			a_type = a_value.__class__.__name__
			return ":%s,%s" % (a, a_type)
		else:
			return ""
	elif type(a) is ListType: # ListType is not hashable
		return ":anonymous_list,%s" % (a)
	else:
		print "Unexpected type for %s: %s" % (a, type(a))
		return ""


def traceit(frame, event, arg):

	#http://docs.python.org/library/sys.html#sys.settrace
	#http://docs.python.org/library/inspect.html
	if event == "call" or event == "return":
		filename = frame.f_code.co_filename
		if filename[0:len(TRACE_BASE)] == TRACE_BASE:

			frame_info = inspect.getframeinfo(frame)
			file_path = frame_info.filename
			if OMIT_PATH:
				dir, file_name = os.path.split(file_path)
			else:
				file_name = file_path

			key = file_name + ":" + str(frame_info.lineno) + ":" + frame_info.function

			if event == "call" and not key in trace_data:
				arg_values = inspect.getargvalues(frame)
				args = ""
				for a in arg_values.args:
					args += describe_arg(a, arg_values)
				trace_data[key] = args
				print key + args
			elif event == "return" and not key in trace_return_data:
				if arg == None:
					trace_return_data[key] = ":" "void"
				else:
					trace_return_data[key] = ":" + arg.__class__.__name__

	return traceit


def save_trace(trace_dict, extension):
	current_dir = os.getcwd() + "/"
	prev_file = None
	output = None

	for key, value in trace_dict.iteritems():
		current_file, tail = key.split(":", 1)

		if current_file != prev_file:
			if output is not None:
				output.close()

			if OMIT_PATH:
				current_file_path = current_dir + current_file
			else:
				current_file_path = current_file

			output = open(current_file_path + extension, "w")

			prev_file = current_file

		pair_string = key + value + "\n"
		output.write(pair_string)

	if output is not None:
		output.close()

if __name__ == '__main__':
	print "starting"
	sys.settrace(traceit)

	main(sys.argv[1:])

	save_trace(trace_data, TRACE_FILE_EXT)
	save_trace(trace_return_data, TRACE_RETURN_FILE_EXT)

