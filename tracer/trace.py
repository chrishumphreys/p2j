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
from gameengine import *

TRACE_BASE = "/home/chris/ab/gamemenu.py"

trace_data = dict()

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
					if a != "self":
						args += ":%s,%s" % (a, arg_values.locals[a].__class__.__name__)
			

				trace_data[key] = args
				print "%s:%d:%s%s" % (frame_info.filename, frame_info.lineno, frame_info.function, args)

	return traceit


if __name__ == '__main__':
	print "starting"
	sys.settrace(traceit)

	main(sys.argv[1:])	

