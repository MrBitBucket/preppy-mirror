# copyright ReportLab Inc. 2000-2002
# see license.txt for license details

# Tests of various functions and algorithms in preppy.
# no side-effects on file system, run anywhere.
# $Header: /rl_home/xxx/repository/rlextra/preppy/test/check_algorithms.py,v 1.1 2002/12/28 22:03:00 andy Exp $
# $Author: andy $ 
# $Date: 2002/12/28 22:03:00 $


import os, glob, string, random
from rlextra.preppy import preppy
from reportlab.test import unittest

class TextFunctionTestCase(unittest.TestCase):
    "Invariant tests for text handlign and substitution functions"

    def checkHealthyColonFunction(self):
        "ensure things in for/while/if blocks get a colon added"
        assert preppy.proctologist('  \t for elem in list:  ') == 'for elem in list:'
        assert preppy.proctologist('for elem in list') == 'for elem in list:'

        
        
        
class GeneratedCodeTestCase(unittest.TestCase):
    """Maybe the simplest and most all-encompassing:
    take a little prep file, compile, exec, and verify that
    output is as expected.  This should catch gross failures
    of preppy """

    def getRunTimeOutput(self, prepCode, **params):
        "compile code, run with parameters and collect output"
        
        pyCode = preppy.PreProcessor().getPythonSource(prepCode)

        # this way of making a module should work back to 1.5.2
        # nowadays 'new.module' would be preferable for clarity
        ns = {}
        exec pyCode in ns
        run = ns['run']

        collector = []
        run(params, __write__=collector.append)
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


class OutputModeTestCase(unittest.TestCase):
    """Checks all ways of generating output return identical
    results - grab string, file"""

    def checkOutputModes(self):
        "compile code, run with parameters and collect output"
        prepCode = "Hello, my name is {{name}} and I am a " \
                   "{{if sex=='m'}}guy{{elif sex=='f'}}gal{{else}}neuter{{endif}}."

        params = {'name':'fred','sex':'m'}
        
        pyCode = preppy.PreProcessor().getPythonSource(prepCode)

        # this way of making a module should work back to 1.5.2
        # nowadays 'new.module' would be preferable for clarity
        ns = {}
        exec pyCode in ns
        run = ns['run']
        getOutput = ns['getOutput']

        # use write function        
        collector = []
        run(params, __write__=collector.append)
        output1 = string.join(collector,'')

        #use file-like object
        from reportlab.lib.utils import getStringIO
        buf = getStringIO()
        run(params, outputfile=buf)
        output2 = buf.getvalue()
        assert output1 == output2, '__write__ and outputfile results differ'

        output3 = getOutput(params)
        assert output3 == output2, 'getOutput(...) and outputfile results differ'
        

        



if __name__=='__main__':
    runner = unittest.TextTestRunner()
    suite1 = unittest.makeSuite(TextFunctionTestCase,'check')
    suite2 = unittest.makeSuite(GeneratedCodeTestCase,'check')
    suite3 = unittest.makeSuite(OutputModeTestCase,'check')
    suite = unittest.TestSuite((suite1, suite2, suite3))
    runner.run(suite)
        
    
