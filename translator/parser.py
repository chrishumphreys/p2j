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

import ast
import os
import re

from visitor import *
from args import *


class Parser():

	def __init__(self, arg_trace, python_filename):
		self.arg_trace = arg_trace
		self.python_filename = python_filename
		self.comment_regex = re.compile('(\s*)(?:(\S.*))?#(.*)')

	def parse_to_string(self, code):
		e = StringEmitter()
		self.parse(code, e)
		e.finish()
		return e.as_string()

	def parse(self, code, e):
		code = self.preprocess_comments(code)
		node = ast.parse(code)
		v = MyVisitor(self.arg_trace, self.python_filename)
		v.visit(node)

		java = v.finish()
		java.emit(e)



	def preprocess_comments(self, code):
		# The parser strips comments delimited with hash so replace with quotes (unless within comment already)
		lines = code.split('\n')
		in_comment = False

		for l in range(0,len(lines)):
			this_line = lines[l]
			num_quotes = len(this_line.split("\"\"\""))
			if num_quotes % 2 == 0:
				# odd number of quotes - therefore toggle in/out of comment
				in_comment = not in_comment

			if not in_comment:
				#This is a crude hack to avoid "#123456" hex strings
				skip = this_line.find("\"#") > -1 or this_line.find("'#") > -1
				if not skip:
					parts = this_line.split("#")
					if len(parts) > 1:
						m = self.comment_regex.match(this_line)
						if m:
							if m.group(1):
								white_space = m.group(1)
							else:
								white_space = ''
							if m.group(2):
								code = m.group(2)
							else:
								code = ''
							comment = m.group(3)
							newline = white_space + code + "\n" + white_space + "\"\"\" " + comment + " \"\"\""
							lines[l] = newline
				
		code = "\n".join(lines)
		#print code
		return code


class StringEmitter():

	def __init__(self):
		self.code_line = ""
		self.lines = [] 

	def emit(self, fragment) :
		if isinstance(fragment, basestring):
			self.code_line = self.code_line + fragment
		else:
			self.code_line = self.code_line + str(fragment)

	def emit_new_line(self):
		self.lines.append(self.code_line)
		self.code_line = ""

	def emit_line(self, fragment) :
		self.emit(fragment)
		self.emit_new_line()

	def as_string(self):
		s = ""
		for l in self.lines:
			s = s + l
			s = s + "\n"
		return s

	def class_start(self, name):
		pass	

	def class_end(self):
		pass

	def clear(self):
		self.lines = [] 

	def finish(self):
		pass

class OutputEmitter(StringEmitter):
	def __init__(self, path):
		StringEmitter.__init__(self)
		self.path = path
		self.class_name = "Default"
		self.code_ext = ".java"

		self.output = open(self.path + "/" + self.class_name + self.code_ext, "w")

	def class_start(self, name):
		self.class_name = name
		self.output_finish()
		self.output = open(self.path + "/" + self.class_name + self.code_ext, "w")
		print "Start class %s" % name

	def class_end(self):
		print self.as_string()
		self.output_finish()
		self.clear()
		print "End class %s" % self.class_name
		self.class_name = "Default"
		self.output = open(self.path + "/" + self.class_name + self.code_ext, "w")

	def output_finish(self):
		self.output.write(self.as_string())
		self.output.close()

	def finish(self):
		self.output_finish()
