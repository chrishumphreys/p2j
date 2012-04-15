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

class ArgTrace:


	def __init__(self):
		self.args = dict()


	def add_trace(self, trace_line):
		last_char = trace_line[-1:]
		if last_char == "\n":
			trace_line = trace_line[0:-1]
		parts = trace_line.split(":")
		filename = parts[0]
		line = parts[1]
		method = parts[2]
		key = filename + ":" + line + ":" + method
		self.args[key] = dict()

		for a in range(3, len(parts)):
			arg = parts[a].split(",")
			name = arg[0]
			typ = arg[1]
			self.args[key][name] = typ

	def find_method_args(self, filename, line, method):
		key = filename + ":" + str(line) + ":" + method
		if key in self.args:
			print "DEBUG: %s found" % key
			return self.args[key]
		else:
			print "WARNING: %s not found" % key
		return None

	def find_method_arg(self, filename, line, method, name):
		args = self.find_method_args(filename, line, method)
		if args and name in args:
			return args[name]
		return None


	@staticmethod
	def load_trace_file(trace_file):
		args = ArgTrace()		
		with open(trace_file) as f:
			line = f.readline()
	                while line:
        	                args.add_trace(line)
				line = f.readline()
		return args
