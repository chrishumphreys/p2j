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

class JavaBase():
	def __init__(self, line_num=0, emit_line_numbers=False):
		self.line_num = line_num
		self.emit_line_numbers = emit_line_numbers

	def emit_base(self, e):
		e.set_source_line(self.line_num)
	
	def emit_comment(self, e):
		self.emit_base(e)
		self.emit_comment_without_base(e)

	def emit_comment_without_base(self, e):
		comment_emitted = False
		is_fresh_line = e.is_fresh_line()

		line_comments = e.line_comments

		if self.line_num > 0 and self.line_num in line_comments:
			if not is_fresh_line: 
				e.emit(" ")
			e.emit_comment("//" + line_comments[self.line_num], self.line_num)
			comment_emitted = True

		if self.emit_line_numbers and self.line_num > 0:
			if not is_fresh_line or comment_emitted: 
				e.emit(" ")
			e.emit("//"" Line " + str(self.line_num))
			comment_emitted = True

		return comment_emitted


	def emit_comment_and_new_line(self, e):
		comment_emitted = self.emit_comment(e)
		e.emit_new_line()
		return comment_emitted

	def emit_line_with_comment(self, e, fragment):
		e.emit(fragment)
		comment_emitted = self.emit_comment(e)
		e.emit_new_line()
		return comment_emitted

	def set_metadata(self, node):
		lineno = node.lineno
		self.line_num = lineno


class JavaClass(JavaBase):

	def __init__(self, name, supers, body):
		JavaBase.__init__(self)
		self.name = name
		self.supers = supers
		self.functions = body
		body.set_parent(self)

	def emit(self, e):
		self.emit_base(e)

		e.emit("public class ")
		e.emit(self.name)

		if self.supers and len(self.supers) > 0:
			e.emit(" extends ")
			self.supers.emit(e)

		self.emit_line_with_comment(e, " {")
		self.functions.emit(e)
		
		e.emit_line("}")
		e.class_end()
		return True


class JavaFunction(JavaBase):

	def __init__(self, name, args, body):
		JavaBase.__init__(self)
		self.name = name
		self.args = args
		self.body = body
		self.class_name = None

	def emit(self,e):
		self.emit_base(e)

		if self.is_constructor():
			e.emit("public ")
			e.emit(self.class_name)			
		else:
			if self.args.list_contains_self():
				e.emit("public void ")
			else:					
				e.emit("public static void ")
			e.emit(self.name)
		e.emit("(")
		self.args.emit(e, True)
		self.emit_line_with_comment(e, ") {")
		self.body.emit(e)
		e.emit_line("}")
		return True

	def set_class(self, clazz):
		self.class_name = clazz.name

	def is_constructor(self):
		return self.name == '__init__'

class JavaAssign(JavaBase):

	def __init__(self, target, value):
		JavaBase.__init__(self)
		self.target = target
		self.value = value


	def emit(self,e):
		self.emit_base(e)

		#Check whether target handles assignment e.g. s['d'] = val which becomes s.get('d', val)
        	swallowAssign = getattr(self.target, "swallows_assign", None)
		if swallowAssign:
			if swallowAssign():
				#allow the target to process the assignment...
				self.target.emit_store(e, self.value)
		else:
			#process the assignment in the normal manner...
			self.target.emit(e)
			e.emit(" = ")
			self.value.emit(e)

		self.emit_line_with_comment(e, ";")

		return True

	def default_swallow_assign(self):
		return False

class JavaAugAssign(JavaBase):

	def __init__(self, target, value, op):
		JavaBase.__init__(self)
		self.target = target
		self.value = value
		self.op = op


	def emit(self,e):
		self.emit_base(e)

		self.target.emit(e)
		self.op.emit(e)
		e.emit("= ")
		self.value.emit(e)
		self.emit_line_with_comment(e, ";")
		return True


class JavaBinOp(JavaBase):

	def __init__(self, left, right, op):
		JavaBase.__init__(self)
		self.left = left
		self.right = right
		self.op = op

	def emit(self,e):
		self.emit_base(e)

		#Check whether op handles arguments e.g. 
        	swallowsBinOp = getattr(self.op, "swallows_binop", None)
		if swallowsBinOp and swallowsBinOp(self.left) :
			self.op.emit_with_args(self.left, self.right, e)
		else:
			# Add parenthesis if parent is a BinOp of higher precedence...
			e.emit("(")
			self.left.emit(e)
			self.op.emit(e)
			self.right.emit(e)
			e.emit(")")
		return False

class JavaBoolOp(JavaBinOp):

	def __init__(self, values, op):
		self.values = values
		self.op = op

	def emit(self,e):
		self.values.list[0].emit(e)
		for o in range(1,len(self.values.list)):
			self.op.emit(e)
			self.values.list[o].emit(e)
		return False


class JavaValueList(JavaBase):
	def __init__(self, contents):
		JavaBase.__init__(self)
		self.contents = contents

	def emit(self,e):
		self.emit_base(e)
		
		if self.contents and len(self.contents.list) > 0:
			e.emit("Arrays.asList({")
			length = len(self.contents.list)
			for c in range(0, length):
				self.contents.list[c].emit(e)
				if c < length-1:
					e.emit(", ")
			e.emit("})")
		else:
			e.emit("new ArrayList()")
		return False


class JavaBinaryOperator(JavaBase):
	def __init__(self, op):
		JavaBase.__init__(self)
		self.op = op

	def emit(self,e):
		self.emit_base(e)
		e.emit(self.op)
		return False

class JavaAnd(JavaBinaryOperator):

	def __init__(self):
		JavaBinaryOperator.__init__(self, "&&")

class JavaGt(JavaBinaryOperator):

	def __init__(self):
		JavaBinaryOperator.__init__(self, ">")

class JavaGte(JavaBinaryOperator):

	def __init__(self):
		JavaBinaryOperator.__init__(self, ">=")

class JavaLt(JavaBinaryOperator):

	def __init__(self):
		JavaBinaryOperator.__init__(self, "<")

class JavaLte(JavaBinaryOperator):

	def __init__(self):
		JavaBinaryOperator.__init__(self, "<=")

class JavaOr(JavaBinaryOperator):

	def __init__(self):
		JavaBinaryOperator.__init__(self, "||")


class JavaBitXor(JavaBinaryOperator):

	def __init__(self):
		JavaBinaryOperator.__init__(self, "^")

class JavaBitOr(JavaBinaryOperator):

	def __init__(self):
		JavaBinaryOperator.__init__(self, "|")


class JavaBitAnd(JavaBinaryOperator):

	def __init__(self):
		JavaBinaryOperator.__init__(self, "&")

class JavaAdd(JavaBinaryOperator):

	def __init__(self):
		JavaBinaryOperator.__init__(self, "+")

class JavaSub(JavaBinaryOperator):

	def __init__(self):
		JavaBinaryOperator.__init__(self, "-")

class JavaMult(JavaBinaryOperator):

	def __init__(self):
		JavaBinaryOperator.__init__(self, "*")

class JavaMod(JavaBinaryOperator):

	def __init__(self):
		JavaBinaryOperator.__init__(self, "%")


	#Check for string % args (special case for Mod)
	def swallows_binop(self, left):
		return isinstance(left, JavaStr)

	#handle string format
	def emit_with_args(self, left, right, e):
		e.emit("String.format(")
		left.emit(e)
		e.emit(", ")
		right.emit(e)
		e.emit(")")

		return False

class JavaDiv(JavaBinaryOperator):

	def __init__(self):
		JavaBinaryOperator.__init__(self, "/")


class JavaVariable(JavaBase):

	def __init__(self, name, context):
		JavaBase.__init__(self)
		self.name = name
		self.context = context
		self.type_name = None

	def emit(self,e):
		self.emit_base(e)

		if self.type_name:
			e.emit(self.type_name)
			e.emit(" ")
		if self.name == 'True':
			e.emit("true")
		elif self.name == 'False':
			e.emit("false")
		elif self.name == 'self':
			e.emit("this")
		elif self.name == 'None':
			e.emit("null")
		else:
			e.emit(self.name)
		return False

	def is_self(self):
		return self.name == 'self'

	def set_type(self, typename):
		self.type_name = typename	

class JavaNum(JavaBase):
	def __init__(self, val):
		JavaBase.__init__(self)
		self.value = val

	def emit(self, e):
		self.emit_base(e)
		e.emit(self.value)
		return False

class JavaStr(JavaBase):
	def __init__(self, val):
		JavaBase.__init__(self)
		self.value = val

	def emit(self, e):
		self.emit_base(e)
		e.emit('"')
		e.emit(self.value) 
		e.emit('"')
		return False

	def emit_comment(self, e):
		self.emit_base(e)
		if self.value.find("\n") > -1:
			e.emit('/*')
			e.emit(self.value) 
			e.emit("*/")
		else:
			e.emit("//")
			e.emit(self.value)
		return False

class JavaList(JavaBase):
	def __init__(self):
		JavaBase.__init__(self)
		self.list = []

	def add(self, obj):
		self.list.append(obj)

	def emit(self,e, skip_self = False):
		self.emit_base(e)
		# Don't always need these parenthesis
		if self._parenthesis():
			e.emit("(")
		for i in range(0, len(self.list)):
			if not (skip_self and self._item_is_self(i)):
				self.list[i].emit(e)
				if i < len(self.list)-1:
					e.emit(", ")
		if self._parenthesis():
			e.emit(")")
		return False
		
	def _parenthesis(self):
		return False

	def __len__(self):
		return len(self.list)

	def _item_is_self(self, i):
		# check for self in argument list
		return isinstance(self.list[i], JavaVariable) and self.list[i].is_self()

	def list_contains_self(self):
		for i in range(0, len(self.list)):
			if self._item_is_self(i):
				return True
		return False

class JavaTuple(JavaList):
	def __init__(self):
		JavaList.__init__(self)
		self.name = "anonymous_list"
		self.type_name = None

	def set_type(self, typename):
		self.type_name = typename


class JavaArgsList(JavaList):
	def __init__(self):
		JavaList.__init__(self)

	def _parenthesis(self):
		return True


class JavaStatements(JavaBase):
	def __init__(self):
		JavaBase.__init__(self)
		self.list = []

	def add(self, obj):
		self.list.append(obj)

	def emit(self,e):
		self.emit_base(e)
		for i in range(0, len(self.list)):
			newline = False
			#This is a hack to attempt to deal with comments which appear as
			#JavaStr objects within statements - something real strings can't 
			#be (for valid code)
			if isinstance(self.list[i], JavaStr):
				newline = self.list[i].emit_comment(e)
				#Only output a newline after statement if object didn't itself
				if not newline:
					e.emit_new_line()
			else:
				if isinstance(self.list[i], JavaClass):
					e.class_start(self.list[i].name)

				newline = self.list[i].emit(e)
				#Only output a newline after statement if object didn't itself
				if not newline:
					e.emit(";")
					if self.line_num > 0:
						self.list[i].emit_comment(e)
					else:
						self.emit_comment(e)
					e.emit_new_line()

	def set_parent(self, parent):
		for i in range(0, len(self.list)):
			if isinstance(self.list[i], JavaFunction):
				self.list[i].set_class(parent)
		
class JavaIf(JavaBase):
	def __init__(self, test, body, orelse):
		JavaBase.__init__(self)
		self.test = test
		self.body = body
		self.orelse = orelse

	def emit(self,e):
		self.emit_base(e)
		e.emit("if (")
		self.test.emit(e)
		self.emit_line_with_comment(e, ") {")
		self.body.emit(e)
		if self.orelse:
			e.emit_line("} else {")
			# CHANGEME: We are currently missing comments for else: lines
			self.orelse.emit(e)
			e.emit_line("}")
		else:
			e.emit_line("}")
		return True

class JavaCall(JavaBase):
	def __init__(self, name, args):
		JavaBase.__init__(self)
		self.name = name
		self.args = args

	def emit(self, e):
		self.emit_base(e)
		self.name.emit(e)
		e.emit("(")
		self.args.emit(e)
		e.emit(")")
		return False

class JavaCompare(JavaBase):
	def __init__(self, left, ops, comparators):
		JavaBase.__init__(self)
		self.left = left
		self.ops = ops
		self.comparators = comparators

	def emit(self, e):
		self.emit_base(e)
		#Check whether op handles the arguments e.g. 'd' in s which becomes s.contains('d')
        	swallowArguments = getattr(self.ops, "swallows_arguments", None)
		if swallowArguments:
			if swallowArguments():
				#allow the target to process the arguments...
				self.ops.emit(e, self.comparators, self.left)
		else:
			#Process the op normally
			self.left.emit(e)
			self.ops.emit(e)
			self.comparators.emit(e)
			return False


class JavaNotEq(JavaBinaryOperator):

	def __init__(self):
		JavaBinaryOperator.__init__(self, " != ")

	def swallows_arguments(self):
		return True

	def emit(self, e, comparators, left):
		if isinstance(left, JavaNum)  or isinstance(comparators, JavaNum):
			#assume primitive !=
			left.emit(e)
			e.emit(" != ")
			comparators.emit(e)			
		else:
			#Be safe than sorry - assume object based equals
			#will fail to compile for primitive
			e.emit("!")
			left.emit(e)
			e.emit(".equals(")
			comparators.emit(e)
			e.emit(")")


class JavaEq(JavaBinaryOperator):

	def __init__(self):
		JavaBinaryOperator.__init__(self, " == ")

	def swallows_arguments(self):
		return True

	
	def emit(self, e, comparators, left):
		if isinstance(left, JavaNum) or isinstance(comparators, JavaNum):
			#assume primitive ==
			left.emit(e)
			e.emit(" == ")
			comparators.emit(e)			
		else:
			#Be safe than sorry - assume object based equals
			#will fail to compile for primitives
			left.emit(e)
			e.emit(".equals(")
			comparators.emit(e)
			e.emit(")")

class JavaNotIn(JavaBase):

	def emit(self, e, comparators, left):
		self.emit_base(e)
		e.emit("!")
		comparators.emit(e)
		e.emit(".contains(")
		left.emit(e)
		e.emit(")")

	def swallows_arguments(self):
		return True

class JavaIn(JavaBase):

	def emit(self, e, comparators, left):
		self.emit_base(e)
		comparators.emit(e)
		e.emit(".contains(")
		left.emit(e)
		e.emit(")")

	def swallows_arguments(self):
		return True



class JavaAttribute(JavaBase):
	def __init__(self, value, attr):
		JavaBase.__init__(self)
		self.value = value
		self.attr = attr
	def emit(self, e):
		self.emit_base(e)
		self.value.emit(e)
		e.emit(".")
		e.emit(self.attr)
		return False		

class JavaReturn(JavaBase):
	def __init__(self, value):
		JavaBase.__init__(self)
		self.value = value

	def emit(self, e):
		self.emit_base(e)
		if self.value:	
			e.emit("return ")
			self.value.emit(e)
		else:
			e.emit("return")
		return False

class JavaSubscript(JavaBase):
	def __init__(self, value, jslice, store):
		JavaBase.__init__(self)
		self.value = value
		self.jslice = jslice
		self.store = store

	def emit(self, e):
		self.emit_base(e)
		self.value.emit(e)
		if isinstance(self.jslice, JavaSlice):
			self.jslice.emit(e)			
		else:
			if self.store:
				e.emit(".put(")
			else:
				e.emit(".get(")
			self.jslice.emit(e)
			e.emit(")")
		return False

	def emit_store(self, e, value):
		self.emit_base(e)
		self.value.emit(e)
		e.emit(".put(")
		self.jslice.emit(e)
		e.emit(", ")
		value.emit(e)
		e.emit(")")
		return False

	def swallows_assign(self):
		return True


class JavaSlice(JavaBase):
	def __init__(self, lower, upper, step):
		JavaBase.__init__(self)
		self.upper = upper
		self.lower = lower
		self.step = step

	def emit(self, e):
		self.emit_base(e)
		#Assume it is a string - most common case...
		if self.upper:
			e.emit(".subSequence(")
			self.lower.emit(e)
			e.emit(", ")
			self.upper.emit(e)
		else:
			e.emit(".substring(")
			self.lower.emit(e)

		e.emit(")")
		#TODO handle step!
		return False


class JavaFor(JavaBase):
	def __init__(self, target, iterator, body):
		JavaBase.__init__(self)
		self.target = target
		self.iterator = iterator
		self.body = body

	def emit(self, e):
		self.emit_base(e)
		e.emit("for(")
		self.target.emit(e)
		e.emit(":")
		self.iterator.emit(e)
		self.emit_line_with_comment(e, ") {")
		self.body.emit(e)
		e.emit("}")

class JavaPass(JavaBase):
	def emit(self,e):
		self.emit_base(e)
		if self.emit_comment(e):
			e.emit_new_line()

class JavaPrint(JavaBase):
	def __init__(self, values):
		JavaBase.__init__(self)
		self.values = values

	def emit(self,e):
		self.emit_base(e)
		e.emit("System.out.println(")
		self.values.emit(e)
		e.emit(")")

class JavaNot(JavaBinaryOperator):

	def __init__(self):
		JavaBinaryOperator.__init__(self, "!")

class JavaUSub(JavaBinaryOperator):

	def __init__(self):
		JavaBinaryOperator.__init__(self, "-")


class JavaUAdd(JavaBinaryOperator):

	def __init__(self):
		JavaBinaryOperator.__init__(self, "+")


class JavaUnaryOp(JavaBinOp):

	def __init__(self, operand, op):
		self.operand =  operand
		self.op = op

	def emit(self,e):
		self.op.emit(e)
		self.operand.emit(e)
		return False

class JavaTryExcept(JavaBase):

	def __init__(self, body, handlers):
		JavaBase.__init__(self)
		self.body = body
		self.handlers = handlers

	def emit(self,e):
		self.emit_base(e)
		self.emit_line_with_comment(e, "try {")
		self.body.emit(e)
		e.emit("}")
		self.handlers.emit(e)
		return False

class JavaTryFinally(JavaBase):

	def __init__(self, body, finalbody):
		JavaBase.__init__(self)
		self.body = body
		self.finalbody = finalbody

	def emit(self,e):
		self.emit_base(e)
		self.emit_line_with_comment(e, "try {")
		self.body.emit(e)
		e.emit_line("} finally {")
		self.finalbody.emit(e)
		e.emit("}")
		return False


class JavaExceptHandler(JavaBase):
	def __init__(self, name, body):
		JavaBase.__init__(self)
		self.name = name
		self.body = body

	def emit(self,e):
		self.emit_base(e)
		e.emit("catch (")
		self.name.emit(e)
		self.emit_line_with_comment(e, ") {")
		self.body.emit(e)
		e.emit("}")
		return False

class JavaWhile(JavaBase):

	def __init__(self, test, body):
		JavaBase.__init__(self)
		self.body = body
		self.test = test

	def emit(self,e):
		self.emit_base(e)
		e.emit("while ")
		self.test.emit(e)
		self.emit_line_with_comment(e, "{")
		self.body.emit(e)
		e.emit("}")
		return False

class JavaBreak():
	def emit(self, e):
		e.emit("break")
		return False
