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

class ArgTrace:


	def __init__(self):
		self.relative_paths = False
		self.args = dict()
		self.return_types = dict()


	def get_key(self, filename, line, method):
		key = filename + ":" + str(line) + ":" + method
		return key

	def get_parts(self, trace_line):
		last_char = trace_line[-1:]
		if last_char == "\n":
			trace_line = trace_line[0:-1]
		parts = trace_line.split(":")
		return parts

	def get_key_for_parts(self, parts):
		filename = parts[0]
		line = parts[1]
		method = parts[2]

		key = self.get_key(filename, line, method)
		return key


	def add_trace(self, trace_line):
		parts = self.get_parts(trace_line)
		key = self.get_key_for_parts(parts)
		self.args[key] = dict()

		for a in range(3, len(parts)):
			arg = parts[a].split(",")
			name = arg[0]
			typ = arg[1]
			self.args[key][name] = typ

	def add_return_trace(self, trace_line):
		parts = self.get_parts(trace_line)
		key = self.get_key_for_parts(parts)
		self.return_types[key] = parts[3]


	def find_type_data(self, args, file_path, line, method):
		if self.relative_paths:
			dir, filename = os.path.split(file_path)
		else:
			filename = file_path

		key = self.get_key(filename, line, method)
		if key in args:
			print "DEBUG: %s found" % key
			return args[key]
		else:
			print "WARNING: %s not found" % key
		return None

	def find_return_type(self, filename, line, method):
		type_data = self.find_type_data(self.return_types, filename, line, method)
		if type_data is not None:
			return type_data
		else:
			return "unkown_return_type"

	def find_method_args(self, filename, line, method):
		args = self.find_type_data(self.args, filename, line, method)
		return args

	def get_method_arg(self, args, name):
		if args is not None:
			if name in args:
				return args[name]
			else:
				return None
		else:
			# We don't have a trace
			return "unkown_type"


	def load_trace_file(self, trace_file):
		self.load_trace_file_with_callback(trace_file, self.add_trace)

	def load_return_trace_file(self, trace_file):
		self.load_trace_file_with_callback(trace_file, self.add_return_trace)

	def load_trace_file_with_callback(self, trace_file, add_trace_line):
		with open(trace_file) as f:
			line = f.readline()
			while line:
				add_trace_line(line)
				line = f.readline()

	@staticmethod
	def load_trace_files(trace_file_base, trace_ext, return_ext, relative_paths):
		args = ArgTrace()
		args.relative_paths = relative_paths
		args.load_trace_file(trace_file_base + trace_ext)
		args.load_return_trace_file(trace_file_base + return_ext)
		return args

