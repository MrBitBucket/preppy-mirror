#preppy test
import os
from rlextra.preppy import preppy
import glob

from reportlab.test import unittest


class SimpleTestCase(unittest.TestCase):
    def checkScriptTag1(self):
        processTest('sample001')

suite = unittest.makeSuite(SimpleTestCase,'check')
    


def processTest(filename, dict={}):
    root, ext = os.path.splitext(filename)
    outFileName = root + '.html'
    mod = preppy.getModule(root)
    outFile = open(outFileName, 'w')
    mod.run({}, outputfile = outFile)
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
            processTest('sample001')
            print 'please read all sample*.html files'
            sys.exit()
        else:
            print '????'
    else:
        runner = unittest.TextTestRunner()
        runner.run(suite)
        print 'please read all sample*.html files'
        
    
