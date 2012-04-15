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

from trans2 import * 
import unittest

class TestSequenceFunctions(unittest.TestCase):

	def setUp(self):
		self.seq = range(10)

	def test_multi_statements(self):
		code = '''
def abc(a, b):
	c = 1
	d = f
'''
		p = Parser(None, None)
		res = p.parse_to_string(code)
		self.assertEqual('public static void abc(a, b) {\nc = 1;\nd = f;\n}\n', res)

	def test_tuples(self):
		code = '''
def abc(a, b):
	c, d = 1, 2
'''
		p = Parser(None, None)
		res = p.parse_to_string(code)
		self.assertEqual('public static void abc(a, b) {\nc, d = 1, 2;\n}\n', res)

	def test_algebra(self):
		code = '''
def abc(a, b):
	c = 1 * (5 + 2) - 3 / 2
'''
		p = Parser(None, None)
		res = p.parse_to_string(code)
		self.assertEqual('public static void abc(a, b) {\nc = ((1*(5+2))-(3/2));\n}\n', res)

	def test_class(self):
		code = '''
class MyClass(BaseClass):
	def abc(self, a, b):
		self.c = a / b;
'''
		p = Parser(None, None)
		res = p.parse_to_string(code)
		self.assertEqual('public class MyClass extends BaseClass {\npublic void abc(a, b) {\nthis.c = (a/b);\n}\n}\n', res)

	def test_strings(self):
		code = '''
def gdef(self):
	g = "10"
'''
		p = Parser(None, None)
		res = p.parse_to_string(code)
		self.assertEqual('public void gdef() {\ng = "10";\n}\n', res)


	def test_multiple_methods_in_class(self):
		code = '''
class T():

	stat = "h"
	s2 = 2

	def met1(self):
		g = "10"
	def met2(self):
		g = "10"
	def met3(self):
		g = "10"
'''
		p = Parser(None, None)
		res = p.parse_to_string(code)
		self.assertEqual('public class T {\nstat = "h";\ns2 = 2;\npublic void met1() {\ng = "10";\n}\npublic void met2() {\ng = "10";\n}\npublic void met3() {\ng = "10";\n}\n}\n', res)


	def test_multiple_statements_top_level(self):
		code = '''
stat = "h"
s2 = 2

def met1(self):
	g = "10"
def met2(self):
	g = "10"
def met3(self):
	g = "10"
'''
		p = Parser(None, None)
		res = p.parse_to_string(code)
		self.assertEqual('stat = "h";\ns2 = 2;\npublic void met1() {\ng = "10";\n}\npublic void met2() {\ng = "10";\n}\npublic void met3() {\ng = "10";\n}\n', res)


	def test_comments(self):
		code = '''
#a comment
"""
A comment
"""
class Abc():
	#Another comment
	def __init__(self):
		a = "hello"
		b = 'there'
'''
		p = Parser(None, None)
		res = p.parse_to_string(code)
		self.assertEqual('// a comment \n/*\nA comment\n*/\npublic class Abc {\n// Another comment \npublic Abc() {\na = "hello";\nb = "there";\n}\n}\n', res)



	def test_if_else(self):
		code = '''
if something: 
	a=b
	c=d
else:
	e=f
	g=h
'''
		p = Parser(None, None)
		res = p.parse_to_string(code)
		self.assertEqual('if (something) {\na = b;\nc = d;\n} else {\ne = f;\ng = h;\n}\n', res)

	def test_if_elseif(self):
		code = '''
if something: 
	a=b
	c=d
elif somethingelse:
	e=f
	g=h
else:
	z=y
	x=r
'''

		p = Parser(None, None)
		res = p.parse_to_string(code)
		self.assertEqual('if (something) {\na = b;\nc = d;\n} else {\nif (somethingelse) {\ne = f;\ng = h;\n} else {\nz = y;\nx = r;\n}\n}\n', res)


	def test_if_complex_condition(self):
		code = '''
if (aComplex(b) != 3): 
	c=d
'''
		p = Parser(None, None)
		res = p.parse_to_string(code)
		self.assertEqual('if (aComplex(b) != 3) {\nc = d;\n}\n', res)


	def test_call(self):
		code = '''
aComplex(b, c, d)
'''
		p = Parser(None, None)
		res = p.parse_to_string(code)
		self.assertEqual('aComplex(b, c, d);\n', res)

	def test_notEq_primitive(self):
		code = '''
a !=2
'''
		p = Parser(None, None)
		res = p.parse_to_string(code)
		self.assertEqual('a != 2;\n', res)

	def test_notEq_object(self):
		code = '''
a != "test"
'''
		p = Parser(None, None)
		res = p.parse_to_string(code)
		self.assertEqual('!a.equals("test");\n', res)

	def test_Eq_primitive(self):
		code = '''
a ==2
'''
		p = Parser(None, None)
		res = p.parse_to_string(code)
		self.assertEqual('a == 2;\n', res)

	def test_Eq_object(self):
		code = '''
a == "test"
'''
		p = Parser(None, None)
		res = p.parse_to_string(code)
		self.assertEqual('a.equals("test");\n', res)


	def test_nested_comments(self):
		code = '''
"""
	# another comment
	pass
"""
'''
		p = Parser(None, None)
		res = p.parse_to_string(code)
		self.assertEqual('/*\n\t# another comment\n\tpass\n*/\n', res)


	def test_attribute(self):
		code = '''
myobj.mymethod(a, b)
'''
		p = Parser(None, None)
		res = p.parse_to_string(code)
		self.assertEqual('myobj.mymethod(a, b);\n', res)


	def test_return(self):
		code = '''
def a(self):
	return True
'''
		p = Parser(None, None)
		res = p.parse_to_string(code)
		self.assertEqual('public void a() {\nreturn true;\n}\n', res)

	def test_return_no_value(self):
		code = '''
def abc(self):
	return
'''
		p = Parser(None, None)
		res = p.parse_to_string(code)
		self.assertEqual('public void abc() {\nreturn;\n}\n', res)


	def test_augassign(self):
		code = '''
def a():
	b.x -= b.w
	b.x += b.w
	b.x *= b.w
	b.x /= b.w
'''
		p = Parser(None, None)
		res = p.parse_to_string(code)
		self.assertEqual('public static void a() {\nb.x-= b.w;\nb.x+= b.w;\nb.x*= b.w;\nb.x/= b.w;\n}\n', res)

	def test_NotIn(self):
		code = '''
ind = 'last_fire_time' not in data
'''
		p = Parser(None, None)
		res = p.parse_to_string(code)
		self.assertEqual('ind = !data.contains("last_fire_time");\n', res)

	def test_In(self):
		code = '''
ind = 'last_fire_time' in data
'''
		p = Parser(None, None)
		res = p.parse_to_string(code)
		self.assertEqual('ind = data.contains("last_fire_time");\n', res)


	def test_Subscript(self):
		code = '''
def a(self):
	if 'last_fire_time' not in data:
		data['last_fire_time'] = time
		time2 = data['last_fire_time']
'''
		p = Parser(None, None)
		res = p.parse_to_string(code)
		self.assertEqual('public void a() {\nif (!data.contains("last_fire_time")) {\ndata.put("last_fire_time", time);\ntime2 = data.get("last_fire_time");\n}\n}\n', res)



	def test_and(self):
		code = '''
a = b and c
'''
		p = Parser(None, None)
		res = p.parse_to_string(code)
		self.assertEqual('a = b&&c;\n', res)

	def test_boolean_multiple_statements(self):
		code = '''
a = b and c and d or e and b > 1 or d < 2
'''
		p = Parser(None, None)
		res = p.parse_to_string(code)
		self.assertEqual('a = b&&c&&d||e&&b>1||d<2;\n', res)


	def test_or(self):
		code = '''
a = b or c
'''
		p = Parser(None, None)
		res = p.parse_to_string(code)
		self.assertEqual('a = b||c;\n', res)


	def test_string_slice_no_step(self):
		code = '''
current_state[0:3]
'''
		p = Parser(None, None)
		res = p.parse_to_string(code)
		self.assertEqual('current_state.subSequence(0, 3);\n', res)

	def test_string_open_ended_slice_no_step(self):
		code = '''
current_state[3:]
'''
		p = Parser(None, None)
		res = p.parse_to_string(code)
		self.assertEqual('current_state.substring(3);\n', res)


	def test_True(self):
		code = '''
a = True
'''
		p = Parser(None, None)
		res = p.parse_to_string(code)
		self.assertEqual('a = true;\n', res)

	def test_False(self):
		code = '''
a = False
'''
		p = Parser(None, None)
		res = p.parse_to_string(code)
		self.assertEqual('a = false;\n', res)


	def test_replaces_self_with_this(self):
		code = '''
self.a = True
'''		
		p = Parser(None, None)
		res = p.parse_to_string(code)
		self.assertEqual('this.a = true;\n', res)

	def test_removes_self_from_arg_list(self):
		code = '''
def a(self):
	pass
'''
		p = Parser(None, None)
		res = p.parse_to_string(code)
		self.assertEqual('public void a() {\n;\n}\n', res)

	def test_static_members(self):
		code = '''
def a():
	pass
'''
		p = Parser(None, None)
		res = p.parse_to_string(code)
		self.assertEqual('public static void a() {\n;\n}\n', res)


	def test_empty_list(self):
		code = '''
rects = []
'''
		p = Parser(None, None)
		res = p.parse_to_string(code)
		self.assertEqual('rects = new ArrayList();\n', res)


	def test_list_strings(self):
		code = '''
rects = ['c', 'b', 'd']
'''
		p = Parser(None, None)
		res = p.parse_to_string(code)
		self.assertEqual('rects = Arrays.asList({"c","b","d"});\n', res)

	def test_list_ints(self):
		code = '''
rects = [1, 2, 3]
'''
		p = Parser(None, None)
		res = p.parse_to_string(code)
		self.assertEqual('rects = Arrays.asList({1, 2, 3});\n', res)


	def test_numeric_mod(self):
		code = '''
a = 1 % 2
'''
		p = Parser(None, None)
		res = p.parse_to_string(code)
		self.assertEqual('a = (1%2);\n', res)

	def test_string_format(self):
		code = '''
a = "blah %s %d" % ("jj", 2)
'''
		p = Parser(None, None)
		res = p.parse_to_string(code)
		self.assertEqual('a = String.format("blah %s %d","jj", 2);\n', res)

	def test_gt(self):
		code = '''
a > 0
'''
		p = Parser(None, None)
		res = p.parse_to_string(code)
		self.assertEqual('a>0;\n', res)

	def test_gte(self):
		code = '''
a >= 0
'''
		p = Parser(None, None)
		res = p.parse_to_string(code)
		self.assertEqual('a>=0;\n', res)


	def test_lt(self):
		code = '''
a < 0
'''
		p = Parser(None, None)
		res = p.parse_to_string(code)
		self.assertEqual('a<0;\n', res)

	def test_lte(self):
		code = '''
a <= 0
'''
		p = Parser(None, None)
		res = p.parse_to_string(code)
		self.assertEqual('a<=0;\n', res)


	def test_renames_constructors(self):
		code = '''
class A:
	def __init__(self):
		pass
'''
		p = Parser(None, None)
		res = p.parse_to_string(code)
		self.assertEqual('public class A {\npublic A() {\n;\n}\n}\n', res)

	def test_pass(self):
		code = '''
def a():
	pass
'''
		p = Parser(None, None)
		res = p.parse_to_string(code)
		self.assertEqual('public static void a() {\n;\n}\n', res)



	def test_for(self):
		code = '''
for u in c_units:
	a=b
	d=e
'''
		p = Parser(None, None)
		res = p.parse_to_string(code)
		self.assertEqual('for(u:c_units) {a = b;\nd = e;\n};\n', res)


	def test_print(self):
		code = '''
print "hello"
'''
		p = Parser(None, None)
		res = p.parse_to_string(code)
		self.assertEqual('System.out.println("hello");\n', res)


	def test_staticmethod_ignored(self):
		code = '''
@staticmethod
def a():
	pass
'''
		p = Parser(None, None)
		res = p.parse_to_string(code)
		self.assertEqual('public static void a() {\n;\n}\n', res)

	def test_not(self):
		code = '''
if not dead:
	pass
'''
		p = Parser(None, None)
		res = p.parse_to_string(code)
		self.assertEqual('if (!dead) {\n;\n}\n', res)

	def test_none_converted_to_null(self):
		code = '''
a = None
'''
		p = Parser(None, None)
		res = p.parse_to_string(code)
		self.assertEqual('a = null;\n', res)


	def test_inline_comment(self):
		code = '''
blah=1 # comment
'''
		p = Parser(None, None)
		res = p.parse_to_string(code)
		self.assertEqual('blah = 1;\n//  comment \n', res)


	def test_tryexception(self):
		code = '''
def a():
	try:
		a=b
		b=c
	except IOError:
		return
	except AA:
		a=b
		return
'''
		p = Parser(None, None)
		res = p.parse_to_string(code)
		self.assertEqual('public static void a() {\ntry{a = b;\nb = c;\n}catch (IOError) {return;\n};\ncatch (AA) {a = b;\nreturn;\n};\n;\n}\n', res)


	def test_tryfinally(self):
		code = '''
try:
	a=b
	b=c
finally:
	a = 0
	b = 0
'''
		p = Parser(None, None)
		res = p.parse_to_string(code)
		self.assertEqual('try{a = b;\nb = c;\n} finally {a = 0;\nb = 0;\n};\n', res)


	def test_while(self):
		code = '''
a = 0
while a:
	a=b
	c=d
'''
		p = Parser(None, None)
		res = p.parse_to_string(code)
		self.assertEqual('a = 0;\nwhile a{a = b;\nc = d;\n};\n', res)


	def test_ignores_strings_with_hash_when_processing_comments(self):
		code = '''
x = "#" + rs + gs + bs
'''
		p = Parser(None, None)
		res = p.parse_to_string(code)
		self.assertEqual('x = ((("#"+rs)+gs)+bs);\n', res)

	def test_ignores_default_arg_values(self):
		code = '''
def tick(self, framerate=0):
	tick = pygame.time.get_ticks()
'''
		p = Parser(None, None)
		res = p.parse_to_string(code)
		self.assertEqual('public void tick(framerate) {\ntick = pygame.time.get_ticks();\n}\n', res)


	def test_bit_or(self):
		code = '''
options = False
options |= True
'''
		p = Parser(None, None)
		res = p.parse_to_string(code)
		self.assertEqual('options = false;\noptions|= true;\n', res)

	def test_bit_and(self):
		code = '''
options = False
options &= True
'''
		p = Parser(None, None)
		res = p.parse_to_string(code)
		self.assertEqual('options = false;\noptions&= true;\n', res)

	def test_bit_xor(self):
		code = '''
options = False
options ^= True
'''
		p = Parser(None, None)
		res = p.parse_to_string(code)
		self.assertEqual('options = false;\noptions^= true;\n', res)



	def test_break(self):
		code = '''
break
'''
		p = Parser(None, None)
		res = p.parse_to_string(code)
		self.assertEqual('break;\n', res)


if __name__ == '__main__':
    unittest.main()



