# Copyright ReportLab Europe Ltd. 2000-2012
# see license.txt for license details

# Tests of various functions and algorithms in preppy.
# no side-effects on file system, run anywhere.
__version__=''' $Id$ '''
import os, glob, string, random
import preppy
import unittest

def P__tokenize(source,filename='<unknown>'):
    P=preppy.PreppyParser(source,filename)
    return P._PreppyParser__tokenize()

def P__preppy(source,filename='<unknown>'):
    P=preppy.PreppyParser(source,filename)
    P._PreppyParser__tokenize()
    return P.dump(P._PreppyParser__preppy())

class PreppyParserTestCase(unittest.TestCase):
    '''test the preppy parser class'''

    def checkTokenize(self):
        self.assertEqual(P__tokenize('Hello World!'),[('const', 1, 0, 12), ('eof', 2, 12, 12)])
        self.assertEqual(P__tokenize('{{1}}'),[('expr', 1, 2, 3), ('eof', 1, 5, 5)])
        self.assertEqual(P__tokenize('{{while 1}}'),[('while', 1, 7, 9), ('eof', 1, 11, 11)])
        self.assertEqual(P__tokenize('{{for i in 1,2}}'),[('for', 1, 5, 14), ('eof', 1, 16, 16)])
        self.assertEqual(P__tokenize('{{if 1}}'),[('if', 1, 4, 6), ('eof', 1, 8, 8)])
        self.assertEqual(P__tokenize('{{script}}a=2{{endscript}}'),[('script', 1, 2, 8), ('const', 1, 10, 13), ('endscript', 1, 15, 24), ('eof', 1, 26, 26)])
        self.assertEqual(P__tokenize('{{script}}a=1\nb=2\nc=3{{endscript}}'), [])

    def check_for(self):
        self.assertEqual(P__preppy('{{for i in 1,2,3}}abcdef{{endfor}}'), "[For(Name('i', Store(), lineno=1, col_offset=7), Tuple([Num(1, lineno=1, col_offset=12), Num(2, lineno=1, col_offset=14), Num(3, lineno=1, col_offset=16)], Load(), lineno=1, col_offset=12), [Expr(Call(Name('__write__', Load(), lineno=1, col_offset=16), [Str('abcdef', lineno=1, col_offset=16)], [], None, None, lineno=1, col_offset=16), lineno=1, col_offset=16)], [], lineno=1, col_offset=3)]")

    def check_while(self):
        self.assertEqual(P__preppy('{{while i<10}}abcdef{{endwhile}}'), "[While(Compare(Name('i', Load(), lineno=1, col_offset=11), [Lt()], [Num(10, lineno=1, col_offset=13)], lineno=1, col_offset=11), [Expr(Call(Name('__write__', Load(), lineno=1, col_offset=12), [Str('abcdef', lineno=1, col_offset=12)], [], None, None, lineno=1, col_offset=12), lineno=1, col_offset=12)], [], lineno=1, col_offset=5)]")

    def check_eval(self):
        self.assertEqual(P__preppy('{{eval}}str.split(\n     "this should show a list of strings")\n{{endeval}}'), "[Expr(Call(Name('__swrite__', Load(), lineno=1, col_offset=6), [Expr(Call(Attribute(Name('str', Load(), lineno=1, col_offset=6), 'split', Load(), lineno=1, col_offset=6), [Str('this should show a list of strings', lineno=2, col_offset=5)], [], None, None, lineno=1, col_offset=6), lineno=1, col_offset=6)], [], None, None, lineno=1, col_offset=6), lineno=1, col_offset=6)]")

    def check_script(self):
        self.maxDiff = None
        self.assertEqual(P__preppy('{{script}}a=1\nb=2\nc=3{{endscript}}'), "[Assign([Name('a', Store(), lineno=1, col_offset=8)], Num(1, lineno=1, col_offset=10), lineno=1, col_offset=8), Assign([Name('b', Store(), lineno=2, col_offset=0)], Num(2, lineno=2, col_offset=2), lineno=2, col_offset=0), Assign([Name('c', Store(), lineno=3, col_offset=0)], Num(3, lineno=3, col_offset=2), lineno=3, col_offset=0)]")

def makeSuite():
    return unittest.TestSuite((unittest.makeSuite(PreppyParserTestCase,'check'),))

if __name__=='__main__':
    runner = unittest.TextTestRunner()
    runner.run(makeSuite())
