"""     
        Written By:
                Chris Humphreys
                Email: < chris (--AT--) habitualcoder [--DOT--] com >
                Jan Weiß
                Email: < jan (--AT--) geheimwerk [--DOT--] de >

        Copyright 2010 Chris Humphreys
        Copyright 2012-2013 Jan Weiß
 
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

from parser import *

if __name__ == '__main__':

	"""
	code = '''
def a():
	for i in w:
		self.weapons |= (i << index)
'''
	"""
	
	p = Parser(None, None)
	e = StringEmitter()
	p.parse(code, e)
	e.finish()

	print "------result------"
	print e.as_string()


#handle calling supers
#packages don't seem to work
#string arrays list don't work
#images = [mygame.Image for x in xrange(0,NUM)]
#break
#<< >>
