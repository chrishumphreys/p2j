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


import sys
import inspect
from types import *
from gameengine import *

TRACE_BASE = "/home/chris/ab/gamemenu.py"

trace_data = dict()


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
	if event == "call":
		filename = frame.f_code.co_filename
		if filename[0:len(TRACE_BASE)] == TRACE_BASE:

			frame_info = inspect.getframeinfo(frame)
			key = frame_info.filename + ":" + str(frame_info.lineno) + ":" + frame_info.function

			if not key in trace_data:
				arg_values = inspect.getargvalues(frame)
				args = ""
				for a in arg_values.args:
					args += describe_arg(a, arg_values)
				trace_data[key] = args
				print "%s:%d:%s%s" % (frame_info.filename, frame_info.lineno, frame_info.function, args)

	return traceit


if __name__ == '__main__':
	print "starting"
	sys.settrace(traceit)

	main(sys.argv[1:])

	#print "%s" % trace_data

