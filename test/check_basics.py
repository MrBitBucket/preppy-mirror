#preppy test
import os, glob, string
from rlextra.preppy import preppy
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
    def check5Escapes(self):
        processTest('sample005')
    def check6NoPythonFile(self):
        mod = preppy.getModule('sample006', savefile=0)
        outFile = open('sample006.html', 'w')
        mod.run(dictionary={}, outputfile = outFile)
        outFile.close()
        print 'wrote sample006.html'

    def check7NoOutputFile(self):
        sourceString = """<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN">
        <HTML>
        <HEAD>
        <TITLE>ReportLab Preppy Test Suite 007</TITLE>
        </HEAD>
        
        <BODY>
        <FONT COLOR=#000000>
        <TABLE BGCOLOR=#0000CC BORDER=0 CELLPADDING=0 CELLSPACING=0 WIDTH=100%>
        <TR>
        <TD>
        <FONT COLOR=#FFFFFF>
        <CENTER>
        <H1>Preppy Test 007 - Creating A Module Without Using The Filesystem</H1>
        </CENTER>
        </FONT>
        </TD>
        </TR>
        </TABLE>
        
        <BR>

        This test creates a preppy source module in memory. It does <I>not</I> have a preppy source file (a file ending in '.prep')
        
        <H2>Expected Output</H2>
        <P>
        
        Below is a listing of the files in the same directory as this HTML file. There should be no file called <I>sample007.prep</I>.
        
        <BR><BR><CENTER>
        <TABLE>
        {{script}}
        import os
        leftColumn = []
        rightColumn = []
        
        fileList = os.listdir(os.getcwd())
        
        for item in range(0,len(fileList),2):
            if os.path.isfile(fileList[item]):
                leftColumn.append(fileList[item])
        
        for item in range(1,len(fileList)-1,2):
            if os.path.isfile(fileList[item]):
                rightColumn.append(fileList[item])
        
        for loopCounter in range(0, len(leftColumn)):
            print "<TR><TD WIDTH=30%>"
            print leftColumn[loopCounter]
            print "</TD>"
            print "<TD WIDTH=30%>"
            try:
                print rightColumn[loopCounter]
                print "</TD></TR>"
            except:
                print " "
                print "</TD></TR>"
                {{endscript}}
        <BR><BR>
        <HR>
        <BR></P>
        
        <CENTER>
        <TABLE>
        <TR><TD>
        
        </TD></TR>
        </TABLE>
        </CENTER>
        
        <BR>
        <HR>
        
        </FONT>
        </BODY>
        </HTML>"""
        
        mod = preppy.getModule("dummy_module", sourcetext=sourceString)
        modDataList=[]
        tempDict={'temp':'temporary variable'}

        # this way it goes to the string
        #import cStringIO
        #f = cStringIO.StringIO()
        #mod.run(tempDict, outputfile=f)
        #f.seek(0)
        #output = f.read()

        #this way it goes to the list and also gets printed        
        mod.run(tempDict, __write__ = modDataList.append)
        print 'length of list is %d' % len(modDataList)
        output=string.join (modDataList,'')
        outFile=open('sample007.html', 'w')
        outFile.write(output)
        outFile.close()
            
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

        else:
            print 'argument not recognised!'
    else:
        runner = unittest.TextTestRunner()
        runner.run(suite)
        print '\nplease read all sample*.html files'
        
    
