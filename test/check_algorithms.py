# Copyright ReportLab Europe Ltd. 2000-2006
# see license.txt for license details

# Tests of various functions and algorithms in preppy.
# no side-effects on file system, run anywhere.
__version__=''' $Id$ '''
import os, glob, string, random
from rlextra.preppy import preppy
import unittest

class GeneratedCodeTestCase(unittest.TestCase):
    """Maybe the simplest and most all-encompassing:
    take a little prep file, compile, exec, and verify that
    output is as expected.  This should catch gross failures
    of preppy """

    def getRunTimeOutput(self, prepCode, quoteFunc=str, **params):
        "compile code, run with parameters and collect output"

        mod=preppy.getModule('test_preppy',savePyc=0,sourcetext=prepCode)

        collector = []
        mod.run(params, __write__=collector.append, quoteFunc=quoteFunc)
        output = string.join(collector,'')
        return output

    def checkStatic(self):
        prepCode = "Hello World"
        out = self.getRunTimeOutput(prepCode)
        self.assertEquals(out, "Hello World")

    def checkExpr1(self):
        prepCode = "Hello {{2+2}} World"
        out = self.getRunTimeOutput(prepCode)
        self.assertEquals(out, "Hello 4 World")

    def checkWhitespaceRespected1(self):
        prepCode = "{{2+2}} " # 1 trailing space
        out = self.getRunTimeOutput(prepCode)
        self.assertEquals(out, "4 ")

    def checkWhitespaceRespected2(self):
        prepCode = "  \t \r{{2+3}}\n " # 1 trailing space
        out = self.getRunTimeOutput(prepCode)
        self.assertEquals(out, "  \t \r5\n ")

    def checkIfStatement1(self):
        prepCode = "Hello, my name is {{name}} and I am a " \
                   "{{if sex=='m'}}guy{{elif sex=='f'}}gal{{else}}neuter{{endif}}."

        out = self.getRunTimeOutput(prepCode, name='fred',sex='m')
        self.assertEquals(out, "Hello, my name is fred and I am a guy.")

        out = self.getRunTimeOutput(prepCode, name='fred',sex='m')
        self.assertEquals(out, "Hello, my name is fred and I am a guy.")

        out = self.getRunTimeOutput(prepCode, name='fred',sex='m')
        self.assertEquals(out, "Hello, my name is fred and I am a guy.")

    def checkFuncWithSideEffects(self):
        prepLines = []
        prepLines.append('{{script}}l = [1, 2]{{endscript}}')
        prepLines.append('{{l.pop()}},')
        prepLines.append('{{l.pop()}},')
        prepLines.append('{{len(l)}}')
        prepCode = ''.join(prepLines)
        out = self.getRunTimeOutput(prepCode)
        self.assertEquals(out, "2,1,0")

    def checkWhileColon(self):
        self.assertEquals(self.getRunTimeOutput('{{script}}i=2{{endscript}}{{while i>=0:}}{{i}}{{if i}},{{endif}}{{script}}i-=1{{endscript}}{{endwhile}}'), "2,1,0")

    def checkWhileNoColon(self):
        self.assertEquals(self.getRunTimeOutput('{{script}}i=2{{endscript}}{{while i>=0}}{{i}}{{if i}},{{endif}}{{script}}i-=1{{endscript}}{{endwhile}}'), "2,1,0")

    def checkForColon(self):
        self.assertEquals(self.getRunTimeOutput('{{for i in (1,2,3):}}{{i}}{{if i!=3}},{{endif}}{{endfor}}'), "1,2,3")

    def checkForNoColon(self):
        self.assertEquals(self.getRunTimeOutput('{{for i in (1,2,3)}}{{i}}{{if i!=3}},{{endif}}{{endfor}}'), "1,2,3")

    def checkIfColon(self):
        self.assertEquals(self.getRunTimeOutput('{{if 1:}}1{{endif}}'), "1")

    def checkIfNoColon(self):
        self.assertEquals(self.getRunTimeOutput('{{if 1}}1{{endif}}'), "1")

    def checkIndentingWithComments(self):
        self.assertEquals(self.getRunTimeOutput('''{{script}}
        #
            i=0
                #
            i=1
    #
        {{endscript}}{{i}}'''),"1")

    def checkForVars(self):
        self.assertEquals(self.getRunTimeOutput('{{i}}{{for i in (1,2,3)}}{{i}}{{if i!=3}},{{endif}}{{endfor}}',i='A'), "A1,2,3")

    def checkLoopVars(self):
        self.assertEquals(self.getRunTimeOutput('{{i}}{{"".join([str(i) for i in (1,2,3)])}}',i='A'), "A123")

    def checkClosingBraces(self):
        self.assertEquals(self.getRunTimeOutput('i}}'), "i}}")

    def checkBackSlashes(self):
        self.assertEquals(self.getRunTimeOutput('{{script}}i=1+2+\\\n\t3{{endscript}}{{i}}'), "6")

    def checkCatchesUnterminated(self):
        self.assertRaises((ValueError,SyntaxError),self.getRunTimeOutput,'{{script}}i=1+2+\\\n\t3{{endscript}}{{i}')

    def checkCatchesIllegalBackSlash(self):
        self.assertRaises((SyntaxError,ValueError),self.getRunTimeOutput,'{{script}}i=1+2+\\ \n\t3{{endscript}}{{i}}')

    def checkQuoting(self):

        #preppy by default does nothing
        source = "<p>{{clientName}}</p>"
        out = self.getRunTimeOutput(source, clientName='Smith & Jones')
        self.assertEquals(out, "<p>Smith & Jones</p>")

        #a quoting function should work on output
        source = "A&B<p>{{clientName}}</p><p>{{script}}print clientName{{endscript}}</p>"
        out = self.getRunTimeOutput(source, clientName='Smith & Jones')
        self.assertEquals(out, "A&B<p>Smith & Jones</p><p>Smith & Jones\n</p>")
        #self.assertEquals(self.getRunTimeOutput('{{script}}v="{{"{{endscript}}{{v}}'), "{{")

        from rlextra.utils.cgisupport import quoteValue
        out = self.getRunTimeOutput(source, clientName='Smith & Jones', quoteFunc=quoteValue)
        #print out
        self.assertEquals(out, "A&B<p>Smith &amp; Jones</p><p>Smith &amp; Jones\n</p>")

        def myQuote(x):
            return x.replace("&", "and")
        out = self.getRunTimeOutput(source, clientName='Smith & Jones', quoteFunc=myQuote)
        self.assertEquals(out, "A&B<p>Smith and Jones</p><p>Smith and Jones\n</p>")

class NewGeneratedCodeTestCase(unittest.TestCase):
    """Maybe the simplest and most all-encompassing:
    take a little prep file, compile, exec, and verify that
    output is as expected.  This should catch gross failures
    of preppy """

    def getRunTimeOutput(self, prepCode, *args,**kwds):
        "compile code, run with parameters and collect output"
        mod=preppy.getModule('test_preppy',savePyc=0,sourcetext=prepCode)
        return mod.get(*args,**kwds)

    def checkNoGet(self):
        self.assertRaises(AttributeError,self.getRunTimeOutput,"Hello World")

    def checkNoArgs(self):
        self.assertEquals(self.getRunTimeOutput("{{def()}}Hello World"), "Hello World")

    def checkNoArgsNeeded(self):
        self.assertRaises(TypeError,self.getRunTimeOutput,"{{def()}}Hello World",1)
        self.assertRaises(TypeError,self.getRunTimeOutput,"{{def()}}Hello World",a=1)

    def checkNoArgsExpr(self):
        self.assertEquals(self.getRunTimeOutput("{{def()}}{{script}}i=5*4{{endscript}}Hello World{{i}}"),
                "Hello World20")

    def checkOneArg(self):
        self.assertEquals(self.getRunTimeOutput("{{def(a)}}Hello World{{a}}",1), "Hello World1")
        self.assertEquals(self.getRunTimeOutput("{{def(a)}}Hello World{{a}}",a=1), "Hello World1")

    def checkOneArgNeeded(self):
        self.assertRaises(TypeError,self.getRunTimeOutput,"{{def(a)}}Hello World{{a}}")
        self.assertRaises(TypeError,self.getRunTimeOutput,"{{def(a)}}Hello World{{a}}",1,2)
        self.assertRaises(TypeError,self.getRunTimeOutput,"{{def(a)}}Hello World{{a}}",b=3)

    def checkBadVar(self):
        self.assertRaises(NameError,self.getRunTimeOutput,"{{def()}}Hello World{{i}}")

    def checkOkVar(self):
        self.assertEquals(
            self.getRunTimeOutput(
                "{{def()}}Hello World{{for i in (1,2)}}{{i}}{{endfor}}"),
            "Hello World12")

    def checkForVar(self):
        self.assertEquals(
            self.getRunTimeOutput(
                "{{def()}}Hello World{{for i in (1,2)}}{{i}}{{endfor}}{{i-2}}"),
            "Hello World120")

    def checkArgs(self):
        self.assertEquals(
            self.getRunTimeOutput(
                "{{def(a,*args)}}Hello World{{a}}{{if args}}{{args}}{{endif}}",1),
            "Hello World1")
        self.assertEquals(
            self.getRunTimeOutput(
                "{{def(a,*args)}}Hello World{{a}}{{if args}}{{args}}{{endif}}",1,2,3),
            "Hello World1(2, 3)")

    def checkKwds(self):
        self.assertEquals(
            self.getRunTimeOutput(
                "{{def(a,**kwds)}}Hello World{{a}}{{if kwds}}{{[k for k in sorted(kwds.items())]}}{{endif}}",1),
            "Hello World1")
        self.assertEquals(
            self.getRunTimeOutput(
                "{{def(a,**kwds)}}Hello World{{a}}{{if kwds}}{{[k for k in sorted(kwds.items())]}}{{endif}}",1,b=2,c=3),
            "Hello World1[('b', 2), ('c', 3)]")

    @staticmethod
    def bracket(x):
        return "[%s]" % x

    @staticmethod
    def brace(x):
        return "{%s}" % x

    def checkLQuoting(self):
        '''__lquoteFunc__ applies to the literals'''
        self.assertEquals(
            self.getRunTimeOutput("{{def()}}Hello World",
                __lquoteFunc__=self.bracket),
                "[Hello World]")

    def checkQuoting(self):
        '''__quoteFunc__ applies to the expressions'''
        self.assertEquals(
            self.getRunTimeOutput("{{def()}}{{script}}i=14{{endscript}}Hello World{{i}}",
                __quoteFunc__=self.brace),
                "Hello World{14}")

    def checkQuotingBoth(self):
        self.assertEquals(
            self.getRunTimeOutput("{{def()}}{{script}}i=14{{endscript}}Hello World{{i}}",
                __quoteFunc__=self.brace, __lquoteFunc__=self.bracket),
                "[Hello World]{14}")
#
#   def checkExpr1(self):
#       prepCode = "Hello {{2+2}} World"
#       out = self.getRunTimeOutput(prepCode)
#       self.assertEquals(out, "Hello 4 World")
#
#   def checkWhitespaceRespected1(self):
#       prepCode = "{{2+2}} " # 1 trailing space
#       out = self.getRunTimeOutput(prepCode)
#       self.assertEquals(out, "4 ")
#
#   def checkWhitespaceRespected2(self):
#       prepCode = "  \t \r{{2+3}}\n " # 1 trailing space
#       out = self.getRunTimeOutput(prepCode)
#       self.assertEquals(out, "  \t \r5\n ")
#
#   def checkIfStatement1(self):
#       prepCode = "Hello, my name is {{name}} and I am a " \
#                  "{{if sex=='m'}}guy{{elif sex=='f'}}gal{{else}}neuter{{endif}}."
#
#       out = self.getRunTimeOutput(prepCode, name='fred',sex='m')
#       self.assertEquals(out, "Hello, my name is fred and I am a guy.")
#
#       out = self.getRunTimeOutput(prepCode, name='fred',sex='m')
#       self.assertEquals(out, "Hello, my name is fred and I am a guy.")
#
#       out = self.getRunTimeOutput(prepCode, name='fred',sex='m')
#       self.assertEquals(out, "Hello, my name is fred and I am a guy.")
#
#   def checkFuncWithSideEffects(self):
#       prepLines = []
#       prepLines.append('{{script}}l = [1, 2]{{endscript}}')
#       prepLines.append('{{l.pop()}},')
#       prepLines.append('{{l.pop()}},')
#       prepLines.append('{{len(l)}}')
#       prepCode = ''.join(prepLines)
#       out = self.getRunTimeOutput(prepCode)
#       self.assertEquals(out, "2,1,0")
#
#   def checkWhileColon(self):
#       self.assertEquals(self.getRunTimeOutput('{{script}}i=2{{endscript}}{{while i>=0:}}{{i}}{{if i}},{{endif}}{{script}}i-=1{{endscript}}{{endwhile}}'), "2,1,0")
#
#   def checkWhileNoColon(self):
#       self.assertEquals(self.getRunTimeOutput('{{script}}i=2{{endscript}}{{while i>=0}}{{i}}{{if i}},{{endif}}{{script}}i-=1{{endscript}}{{endwhile}}'), "2,1,0")
#
#   def checkForColon(self):
#       self.assertEquals(self.getRunTimeOutput('{{for i in (1,2,3):}}{{i}}{{if i!=3}},{{endif}}{{endfor}}'), "1,2,3")
#
#   def checkForNoColon(self):
#       self.assertEquals(self.getRunTimeOutput('{{for i in (1,2,3)}}{{i}}{{if i!=3}},{{endif}}{{endfor}}'), "1,2,3")
#
#   def checkIfColon(self):
#       self.assertEquals(self.getRunTimeOutput('{{if 1:}}1{{endif}}'), "1")
#
#   def checkIfNoColon(self):
#       self.assertEquals(self.getRunTimeOutput('{{if 1}}1{{endif}}'), "1")
#
#   def checkIndentingWithComments(self):
#       self.assertEquals(self.getRunTimeOutput('''{{script}}
#       #
#           i=0
#               #
#           i=1
#   #
#       {{endscript}}{{i}}'''),"1")
#
#   def checkForVars(self):
#       self.assertEquals(self.getRunTimeOutput('{{i}}{{for i in (1,2,3)}}{{i}}{{if i!=3}},{{endif}}{{endfor}}',i='A'), "A1,2,3")
#
#   def checkLoopVars(self):
#       self.assertEquals(self.getRunTimeOutput('{{i}}{{"".join([str(i) for i in (1,2,3)])}}',i='A'), "A123")
#
#   def checkClosingBraces(self):
#       self.assertEquals(self.getRunTimeOutput('i}}'), "i}}")
#
#   def checkBackSlashes(self):
#       self.assertEquals(self.getRunTimeOutput('{{script}}i=1+2+\\\n\t3{{endscript}}{{i}}'), "6")
#
#   def checkCatchesUnterminated(self):
#       self.assertRaises((ValueError,SyntaxError),self.getRunTimeOutput,'{{script}}i=1+2+\\\n\t3{{endscript}}{{i}')
#
#   def checkCatchesIllegalBackSlash(self):
#       self.assertRaises((SyntaxError,ValueError),self.getRunTimeOutput,'{{script}}i=1+2+\\ \n\t3{{endscript}}{{i}}')
#
#   def checkQuoting(self):
#
#       #preppy by default does nothing
#       source = "<p>{{clientName}}</p>"
#       out = self.getRunTimeOutput(source, clientName='Smith & Jones')
#       self.assertEquals(out, "<p>Smith & Jones</p>")
#
#
#       #a quoting function should work on output
#       source = "A&B<p>{{clientName}}</p><p>{{script}}print clientName{{endscript}}</p>"
#       out = self.getRunTimeOutput(source, clientName='Smith & Jones')
#       self.assertEquals(out, "A&B<p>Smith & Jones</p><p>Smith & Jones\n</p>")
#       #self.assertEquals(self.getRunTimeOutput('{{script}}v="{{"{{endscript}}{{v}}'), "{{")
#
#       from rlextra.utils.cgisupport import quoteValue
#       out = self.getRunTimeOutput(source, clientName='Smith & Jones', quoteFunc=quoteValue)
#       #print out
#       self.assertEquals(out, "A&B<p>Smith &amp; Jones</p><p>Smith &amp; Jones\n</p>")
#
#
#       def myQuote(x):
#           return x.replace("&", "and")
#       out = self.getRunTimeOutput(source, clientName='Smith & Jones', quoteFunc=myQuote)
#       self.assertEquals(out, "A&B<p>Smith and Jones</p><p>Smith and Jones\n</p>")

class OutputModeTestCase(unittest.TestCase):
    """Checks all ways of generating output return identical
    results - grab string, file"""

    def checkOutputModes(self):
        "compile code, run with parameters and collect output"
        prepCode = "Hello, my name is {{name}} and I am a " \
                   "{{if sex=='m'}}guy{{elif sex=='f'}}gal{{else}}neuter{{endif}}."

        params = {'name':'fred','sex':'m'}

        mod=preppy.getModule('test_preppy',savePyc=0,sourcetext=prepCode)

        # this way of making a module should work back to 1.5.2
        # nowadays 'new.module' would be preferable for clarity

        # use write function
        collector = []
        mod.run(params, __write__=collector.append)
        output1 = string.join(collector,'')

        #use file-like object
        from reportlab.lib.utils import getStringIO
        buf = getStringIO()
        mod.run(params, outputfile=buf)
        output2 = buf.getvalue()
        assert output1 == output2, '__write__ and outputfile results differ'

        output3 = mod.getOutput(params)
        assert output3 == output2, 'getOutput(...) and outputfile results differ'

class IncludeTestCase(unittest.TestCase):
    def testRequiredArgs(self):
        def args(*args, **stuff):
            return True
        inner = "{{direction}}"
        modInner = preppy.getModule('dummy1',savePyc=0,sourcetext=inner)
        outer = """{{for direction in directions}}{{inner.getOutput({'direction':direction})}}{{endfor}}"""
        modOuter = preppy.getModule('dummy2',savePyc=0,sourcetext=outer)
        ns = {'directions':('NORTH','SOUTH','EAST','WEST'),
              'args':args,
              'inner':modInner}
        output = modOuter.getOutput(ns)
        #self.assertRaises(NameError, modOuter.getOutput, ns)
        self.assertEquals(output, "NORTHSOUTHEASTWEST")

def makeSuite():
    suite1 = unittest.makeSuite(NewGeneratedCodeTestCase,'check')
    suite2 = unittest.makeSuite(GeneratedCodeTestCase,'check')
    suite3 = unittest.makeSuite(OutputModeTestCase,'check')
    suite4 = unittest.makeSuite(IncludeTestCase)
    return unittest.TestSuite((suite1,suite2, suite3, suite4))

if __name__=='__main__':
    runner = unittest.TextTestRunner()
    runner.run(makeSuite())
