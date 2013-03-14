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
been in continual production use since then.  It is open source (BSD-license)

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

At the time, every developer and his dog was busy inventing templating systems
for web development.  Most of these involved coming up with an unreliable parser,
and an incomplete little language for embedding in markup.  We took the view 
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
big and complex.  




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

getModule returns a Python module object. On first call, or when templates change, this will generate a .pyc file. This module contains a function, getOutput, which implements your template.  The template is compiled into a function, which accepts parameters and returns a big (non-Unicode, 8-bit) string.



preppy syntax
--------------







Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

