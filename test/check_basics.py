#preppy test
import os
from rlextra.preppy import preppy
import glob

from reportlab.test import unittest


class SimpleTestCase(unittest.TestCase):
    def check1ScriptTag(self):
        processTest('sample001')
    def check2ForAndWhileLoops(self):
        processTest('sample002')
    def check3IfTags(self):
        processTest('sample003')
    def check4PassingDictionaries(self):
        dictionary = {"song1": {"songtitle": "The Lumberjack Song", "by": "Monthy Python"},
                      "song2": {"songtitle": "My Way", "by": "Frank Sinatra"}}
        processTest('sample004', dictionary)
    def check5Escape(self):
        processTest('sample005')

suite = unittest.makeSuite(SimpleTestCase,'check')

def processTest(filename, dictionary={}):
    root, ext = os.path.splitext(filename)
    outFileName = root + '.html'
    mod = preppy.getModule(root)
    outFile = open(outFileName, 'w')
    mod.run(dictionary, outputfile = outFile)
    outFile.close()
    print 'wrote',outFileName

def clean(dirname='.'):
    for filename in glob.glob('sample*.prep'):
        root, ext = os.path.splitext(filename)
        if os.path.isfile(root + '.html'):
            os.remove(root + '.html')
        if os.path.isfile(root + '.py'):
            os.remove(root + '.py')
        if os.path.isfile(root + '.pyc'):
            os.remove(root + '.pyc')
            
        

if __name__=='__main__':
    import sys
    if len(sys.argv) == 2:
        arg = sys.argv[1]
        if arg == 'clean':
            clean()
            sys.exit()
        elif arg == 'old':
            clean()
            dictionary = {}
            processTest('sample001')
            processTest('sample002')
            processTest('sample003')
            dictionary = {"song1": {"songtitle": "The Lumberjack Song", "by": "Monthy Python"},
                          "song2": {"songtitle": "My Way", "by": "Frank Sinatra"}}
            processTest('sample004', dictionary)
            processTest('sample005')
            print 'please read all sample*.html files'
            sys.exit()
        else:
            print 'argument not recognised!'
    else:
        runner = unittest.TextTestRunner()
        runner.run(suite)
        print 'please read all sample*.html files'
        
    
