# Copyright ReportLab Europe Ltd. 2000-2004
# see license.txt for license details

# Tests of various functions and algorithms in preppy.
# no side-effects on file system, run anywhere.
# $Author$
# $Date$


import os, glob, string, random
from rlextra.preppy import preppy
from reportlab.test import unittest

class GeneratedCodeTestCase(unittest.TestCase):
    """Maybe the simplest and most all-encompassing:
    take a little prep file, compile, exec, and verify that
    output is as expected.  This should catch gross failures
    of preppy """

    def getRunTimeOutput(self, prepCode, **params):
        "compile code, run with parameters and collect output"

        mod=preppy.getModule('test_preppy',savePyc=0,sourcetext=prepCode)

        collector = []
        mod.run(params, __write__=collector.append)
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

if __name__=='__main__':
    runner = unittest.TextTestRunner()
    suite2 = unittest.makeSuite(GeneratedCodeTestCase,'check')
    suite3 = unittest.makeSuite(OutputModeTestCase,'check')
    suite = unittest.TestSuite((suite2, suite3))
    runner.run(suite)
