.. preppy documentation master file, created by
   sphinx-quickstart on Thu Mar 14 21:19:20 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to preppy's documentation!
==================================

Contents:

.. toctree::
   :maxdepth: 2


Why Preppy?
===========

Preppy is ReportLab's templating system.  It was developed in late 2000 and has
been in continual production use since then.  It is open source (BSD-license).

The key features are:

* single Python module.  It's easy to include it in your project
* easy to learn.  It takes about one minute to scan all the features
* it just embeds Python.  We have not invented another language, and if you want to do something - includes, quoting, filters - you just use Python
* compiled to bytecode: a .prep file gets compiled to a Python function in a .pyc file
* easy to debug: preppy generates proper Python exceptions, with the correct line numbers for the .prep file.  You can follow tracebacks from Python script to Preppy template and back, through multiple includes
* familiar.  We've been using {{this}} syntax since well before Django was thought of
* 8-bit safe:  it makes no assumption that you are generating markup and does nothing unexpected with whitespace; you could use it to generate images or binary files if you wanted to.

Since there are dozens of templating systems out there, it's worth explaining
why this one exists.

We developed preppy in 2000.  At the time, every python developer and his dog 
was busy inventing their own web framework, usually including a templating 
system for web development.  

Most of these involved coming up with an unreliable parser, and an incomplete 
'little language' for embedding in markup.  We took the view 
that we already had a perfectly good little language - Python - and there was
no need to invent a new one.  Preppy has met all of our needs well, with minimal
changes.

Our main product is a markup-based system for creating PDF documents, Report
Markup Language &trade;.  When we create reports for people, we use a template
to generate an RML file, in the same way that most people make web pages. We
need a templating system for our own demos and tutorials, as well as solutions
we build, which is 'in the box' and easy to understand.  We also build web
applications, and when we want something strict and minimal, we use preppy.

Moving on, most major web frameworks have settled on a templating system. The
most popular ones, such as Django or Jinja, are very full-featured.  They have
focused on creating a new language for web designers.  They are getting fairly
big and complex and they impose their own learning curve.  THey also result in
template programming becoming a different skill to the main application, and
sometimes with a different philosophy.  For example, in the Django world,
templates are supposed to be coded by designers who lack programming skills,
and are forgiving of errors.

Within ReportLab we take the view that a template is code; it is expected to
be correct, and to raise errors when misspelled or nonexistent variables are
used.  It is far easier to create a robust system when the templates use
the same language, and are debugged in exactly the same way, as the application
code.  

Later on, we'll show how many features of high-end templating systems are handled
with short Python expressions.


Quick Start
===========

using preppy
------------

Place your template code in a file which, by convention, ends in .prep.  Here is an example::

    <html><head><title>{{name}}</title></head><body>
    hello my name is {{name}} and I am
    {{if sex=="f":}} a gal
    {{elif sex=="m":}} a guy
    {{else:}} neuter {{endif}}
    </body></html>

If this is in a file called, say, *template.prep*, you can invoke it like this::

    mymodule = preppy.getModule('template.prep')
    
    namespace = dict('name':'fred','sex':'m')
    html = mymodule.getOutput(namespace)

getModule returns a Python module object. On first call, or when templates are edited, this will generate a .pyc file, just as a Python module does (assuming you have write access to the disk). This module contains a function, *getOutput*, which implements your template.  The function, which accepts parameters and returns a big (non-Unicode, 8-bit) string.

This is preppy's key design idea:  we try to make a preppy template as much like a python function as possible.


preppy syntax
--------------

{{expression}}::

Any Python expression will be evaluated in the current namespace, and thence converted to a string representation.  Examples:

{{2+2}}
{{range(10)}}
{{client.name}}


{{eval}}::

{{eval}}
a_complex("and", "very", "verbose", function="call")
{{endeval}}

This is exactly equivalent to {{expression}}, but is useful when you have a long Python expression which spans several lines, or the extra curly braces on the same line as the expression harm readability.

{{script}}::



Multiple or single lines of python scripts may be embedded within {{script}}...{{endscript}} tags.  Examples:

{{script}}import urllib2{{endscript}}

{{script}}
cur = conn.cursor()
cur.execute('select * from some_table')
data = cur.fetchall()
{{endscript}}

WARNING: for expression, eval, and script any newlines in the code text
will be automatically indented to the proper indentation level for
the run() module at that insertion point.  You may therefore indent your
code block to match the indentation level of any HTML/XML it is embedded in.  This is only a concern for triple quoted strings.  If this may be an issue, don't use triple quoted strings in preppy source. Instead of

x = """
a string
"""

use

x = ("\n"
"\ta string\n"
)

or similar.


It is generally bad practice to have too much in script tags.  If you find yourself writing long script sections to fetch and prepare
data or performing calculations, it is much better to place those things
in a separate python module, import it within the template, and call
those functions in one line.  



{{if}}::

The if statement does exactly what Python's *if* statement does.  You may optionally use multiple *elif* clauses and one *else* clause.

{{if expr}}   ....{{elif expr}} ....{{else}}     {{endif}}


{{for}}::
{{for for_target}} block {{endfor}}

This implements a for loop in preppy source.  The for_target should follow
normal python conventions for python for loops.  The resulting python 
code is roughly

for for_target:
    interpretation_of(block)

{{while}}:

{{while condition}} block {{endwhile}}

This implements a while loop in preppy source.  The condition should be
a python expression.  The resulting python code is roughly

while condition:
    interpretation_of(block)


Module import options
---------------------
There are two ways to load a preppy module into memory.  We refer to these as 'file system semantics' and 'import semantics'.

m = getModule(name, directory=".", source_extension=".prep", 
        verbose=0, savefile=1, sourcetext=None)

There is no predefined search path or list of template directories.  *name* can be a relative or full path. Commonly in web applications we work out the full path to the template directory and do everything with the *name* argument:

m = getModule(os.path.join(PROJECT_DIR, 'myapp/templates/template.prep'))

You can also omit the extension; if none is given; and you can optionally supply a template name and the directory in a separate argument.  Finally, you can supply literal source if desired.

The resulting module should be treated just like a Python module:  import it, keep it around, and call it many times.  


Executing the template
----------------------

The most common approach is



m.getOutput(namespace)


which returns the generated output (usually HTML) as a string.

The full syntax is:

def getOutput(dictionary, quoteFunc=str):


If you prefer a streaming or file-based approach, you can use

def run(dictionary, __write__=None, quoteFunc=str, outputfile=None,code=__code__):

You may either supply a function callback to __write__, which will be called repeatedly with the generated text; or a file-like object to *outputfile*.





Quoting functions
-----------------
By default, preppy will use Python's str function to display any expression.
This causes a problem in the markup world, where output us usually utf-8 encoded.
An expression like this will fail on the first foreign accent in a name,
because Python can't convert this to ASCII.
  {{client.surname}}

Another common use for a quote function is to escape '&' signs, which may well
appear in database fields, and will produce illegal markup.

In general, you should decide on the quoting function you need, and pass it
in when templates are called.

from xml.sax.saxutils import escape  #this escapes '&','<' and '>'
def quote(stuff):
    utf8 = unicode(stuff).encode('utf-8')
    return escape(utf8)

m.getOutput(namespace, quoteFunc=quote)



WARNING: we 




Templates with declarations
---------------------------
In an attempt to make preppy even more like a Python function, we introduced explicit declarations.  This is particularly important when you end up importing nested templates and are not sure what variables are defined in the current namespace.

To use explicit declarations, add a line with {{def ...}} at the top of your template.  This is
supposed to look like a Python function declaration, but without the function name.  It supports
positional and keyword arguments.

{{def data, options}}

This is a declaration that the template will be called with two arguments, 'data' and 'options'.
A programmer asked to do maintenance on the template will generally find this helpful because
they know immediately what is being passed in.

The template must then be called with the shorter *get* function:


m.get(*args, **kwds)

output = m.get(

This is particularly helpful when nesting templates.  In an outer template, you can call another one with a single line, and be clear about what is being passed in:

<h1>Terms and conditions</h1>
{{terms_template.get(data, options)}}


Controlling compilation
-----------------------

In normal use, assuming the current user has write access to the file system, preppy will function like Python:  edit your template, run your program, and the calls to getModule will trigger a recompile.


preppy can also function as a script to let you control compilation. 
In some web frameworks (including CGI-based ones), the application runs as a restricted user, and it is important to precompile all templates and python
modules during deployment.

The command line interface lets you test, compile and clean up:

    preppy modulename [arg1=value1, arg2=value2.....]
       - shorthand for 'preppy run ...', see below.

    preppy run modulename [arg1=value1, arg2=value2.....]
       - runs the module, optionally with arguments.  e.g.
         preppy.py flintstone.prep name=fred sex=m

    preppy.py compile [-f] [-v] [-p] module1[.prep] module2[.prep] module3 ...
       - compiles explicit modules

    preppy.py compile [-f] [-v] [-p] dirname1  dirname2 ...
       - compiles all prep files in directory recursively

    preppy.py clean dirname1 dirname2 ...19
       - removes any py or pyc files created from past compilations


But how do I...?
================

People with experience of bigger templating systems typically wonder where their 
beloved features are.


Include
-------
How do you include other content?  With a Python function or method call.

If you want to include totally static content, it's as easy as this:

<h1>Appendix</h1>
{{open('templates/appendix.html'.read())}}

If you want to call other templates, then import them at the top of the module in
a script tag, and call them inline:

{{script}}
appendix = preppy.getModule('appendix.prep') 
{{endscript}}

<h1>Appendix</h1>
{{appendix.get(data, options)}}

or 

{{appendix.getOutpu(namespace)}}


Automatic escaping
------------------
Many systems can escape all output as a security measure.  Some go further and try to remove Javascript.   Preppy lets you pass in your own quote function.

AR: WE NEED A GLOBAL WAY TO SET THE QUOTE FUNCTION, OR MAYBE CHANGE IT TO UTF8.


Template utilities
------------------
It is bad practice to have hundreds of lines of Python script at the top
of a template.  Python code is easier to write and test in a separate module.
Therefore, for a large template, we commonly end up with a separate Python
module containing utilities for use within the template.

Filters
-------

Django has a nice syntax for filters - functions which tidy up output.

{{number | floatformat}}

Our approach is to have functions with short names.  For example, if a template had to
display many values in pounds sterling, we could write a function *fmtPounds* which
adds the pound sign, formats with commas every thousand and two decimal places.  
These functions can also be set to output an empty string for None or missing values.

We then display like this
<td>{{fmtPounds(total)}}</td>

This approach requires a couple of extra parentheses but is very clear.  It is common
and useful to define these once per application in a helper module and import them.
For example with our own Report Markup Language (used for PDF generation), we will
commonly have a large template called 'rmltemplate.prep', and a helper Python module
'rmlutils.py'.  Developers know that this module contains utilities for use in the
template.






Block inheritance
-----------------
We don't support this.  







Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

