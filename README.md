p2j : A (restricted) python to java source translator
=====================================================

Written By:  
Chris Humphreys  
Email: < chris (--AT--) habitualcoder [--DOT--] com >  
Jan Weiß  
Email: < jan (--AT--) geheimwerk [--DOT--] de >


Intro
-----

This program consists of two parts:

1. A Source translator which attempts to convert Python syntax to the Java equivalent

2. A profiler which uses Python’s Debugger and AST tools to index all run time method 
argument information, used by 1. above during type inference.


Surprisingly these two simple parts are sufficient to translate some simple Python 
to Java.

In its current form the tool will perform about 75% of code translation. The remainder
must be converted manually. A lot of the outstanding syntax errors can be fixed 
semi-automatically with a modern Java IDE. The remainder of the work is dealing
with unsupported concepts (like creating value objects for tuples etc) and porting
library client code to Java equivalents.


Usage
-----

Prepare to get your hands a little dirty…

### Step 1: Capture the trace information for runtime argument types.

Profiling a running program is slow so the tracer is restricted to profiling methods within
a single python source file at a time. On a fast machine you can change this if you like.

#### Assuming you have a python program, started using a main(args) method:

1. Copy “tracer/trace.py” into your application’s directory (the directory of the file where the main(args) method is located).  

2. Edit trace.py and update `TRACE_BASE = "/home/chris/ab/gamemenu.py"` with the path to the python script file you wish to profile. In this example `gamemenu.py`.

3. Change the `import` statement to import everything from the file containing main():  
`from gameengine import *`

4. Run your application using `python trace.py`. Parameters are passed through to your main().

5. Use your application in a normal manner to ‘exercise’ all the methods in the target file.

6. Quit your application.

7. Ensure that both gamemenu.py.trace and gamemenu.py.return-trace have been written.

8. Repeat for all other python source files you wish to convert.


### Step 2: Translate the source files to java

1. Copy all the trace files captured above into the translator directory.

2. Copy all your python source files you wish to translate into the translator directory.

3. Create an output directory within the translator directory:  `mkdir target`

4. Translate each file in turn using a command similar to:  `python translate.py gamemenu.py`

5. Verify your source files have been written to target.

### Step 3: Clean up the generated code

1. Create a new project in your Eclipse IDE and import all the generated source files.

2. Stub out the python library APIs which your code is dependent on and have not been converted.

3. Use your IDE’s tools to infer types of local variables and fields. It should manage this in most
4. cases.

5. Fix up return types manually.

6. Port library client code to Java API equivalents. This is easier to do once the majority of the code is compiling (against your stubs).


Notes about generated code
--------------------------

Each python source file results in a similarly named java package.

Each class within a python source file is written to its own source file

Static procedures and variables within the python file are written to a class called Default.java
within the package. This works as long as all the static content of a file is at the top of the file, 
with only classes following. You may wish to reorder your input source files before translation. 
Alternatively you will find content dispersed through the generated class files which you must move
manually.

Collection generics are not supported. You will have to add the missing type information yourself.

For methods that return tuples or multiple results you will have to create value object classes.



License
-------
This program is licensed under the GNU General Public License v3. See LICENSE for details.



FAQ
---

Q : Is it any good?

A : Possibly. It was written for a specific purpose (converting a Python game to Android)
which it achieved well (http://www.habitualcoder.com/ab/android).

Q : What Python syntax does it support?

A : The simple, imperative constructs (loops/variables), variables, dicts, lists, classes. For
a complete list check the test suite in test.py.
Currently it does not support functional constructs (map/reduce/yield/complex generators etc)

Q : What libraries are supported?

A: The tool makes no attempt to convert libraries. You will have to create facades or convert
client APIs manually.

Q : What support does it have for dynamic typing?

A : Not much. It assumes implicit static typing and uses runtime profiling to determine the types. This currently has some limitations.
Previously it was only supported for method argument (not member, local vars or return types) and worked only if 
the arguments to methods are always the same type. After some hacking, all types that were seen during tracing are collected and injected into the output. This won’t compile of course, but it beats manually inferring the types hands down. This way, you can get a grasp on the types so you can either rewrite your Python code or rework the output. For Java this isn’t as bad as it sounds. A good Java IDE will be able to infer a lot of variable types given known method arguments.

Q : It doesn’t support XYZ! Help.

A : Get in touch, I’ll see what I can do to help.


