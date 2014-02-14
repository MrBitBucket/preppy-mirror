# Copyright ReportLab Europe Ltd. 2000-2012
# see license.txt for license details

# Tests of various functions and algorithms in preppy.
# no side-effects on file system, run anywhere.
__version__=''' $Id$ '''
import os, glob, random, unittest, traceback
import preppy

def checkErrorTextContains(texts,func,*args,**kwds):
    try:
        func(*args,**kwds)
    except:
        if not isinstance(texts,(list,tuple)):
            texts = (texts,)
        buf=preppy.StringIO()
        traceback.print_exc(file=buf)
        buf = buf.getvalue()
        for t in texts:
            if t not in buf:
                return buf
        else:
            return ''
    else:
        return 'An error containing texts\n%s\nwas not raised' % '\n'.join(texts)

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
        output = ''.join(collector)
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
        source = "A&B<p>{{clientName}}</p><p>{{script}}print(clientName){{endscript}}</p>"
        out = self.getRunTimeOutput(source, clientName='Smith & Jones')
        self.assertEquals(out, "A&B<p>Smith & Jones</p><p>Smith & Jones\n</p>")
        #self.assertEquals(self.getRunTimeOutput('{{script}}v="{{"{{endscript}}{{v}}'), "{{")


        def customQuoteFunc(v):
            """Here's a very old, but real, quote function we once used.
            
            Defense against people embedding Javascript in parameters.
            Script kiddies often hope that you will echo through some form
            parameter like a surname in a text field into HTML, so they
            can embed some huge chunk of their own HTMl code in it.
            This ensures any tags in input are escaped and thus deactivated"""

            vs = v.split("&")
            if len(vs)>1:
                # quote ampersands, but not twice
                v = '&'.join([vs[0]]+
                        [((";" not in f or len(f.split(";")[0].split())>1) and 'amp;' or '')+f for f in vs[1:]]
                        )
            return v.replace("<","&lt;").replace(">","&gt;").replace('"',"&quot;").replace("'","&#039;")



        out = self.getRunTimeOutput(source, clientName='Smith & Jones', quoteFunc=customQuoteFunc)
        self.assertEquals(out, "A&B<p>Smith &amp; Jones</p><p>Smith &amp; Jones\n</p>")

        def myQuote(x):
            return x.replace("&", "and")
        out = self.getRunTimeOutput(source, clientName='Smith & Jones', quoteFunc=myQuote)
        self.assertEquals(out, "A&B<p>Smith and Jones</p><p>Smith and Jones\n</p>")

        #Andy's standard quote for django
        source = '<a>{{A}}</a>'
        self.assertEquals(self.getRunTimeOutput(source, A=1.2, quoteFunc=preppy.stdQuote), "<a>1.2</a>")
        self.assertEquals(self.getRunTimeOutput(source, A='<&>', quoteFunc=preppy.stdQuote), "<a>&lt;&amp;&gt;</a>")
        self.assertEquals(self.getRunTimeOutput(source, A=preppy.SafeUnicode('<&>'), quoteFunc=preppy.stdQuote), "<a><&></a>")
        self.assertEquals(self.getRunTimeOutput(source, A=preppy.SafeUnicode('<&>'), quoteFunc=preppy.stdQuote), "<a><&></a>")
        self.assertEquals(self.getRunTimeOutput(source, A=b'\xc2\xae', quoteFunc=preppy.stdQuote), u"<a>\xae</a>")
        self.assertEquals(self.getRunTimeOutput(source, A=None, quoteFunc=preppy.stdQuote), "<a></a>")

    def checkForContinueElse(self):
        source="{{for i in range(3)}}{{if i==C}}{{continue}}{{endif}}{{i}}{{endfor}}"
        self.assertEquals(self.getRunTimeOutput(source, C=-1, quoteFunc=preppy.stdQuote), "012")
        self.assertEquals(self.getRunTimeOutput(source, C=2, quoteFunc=preppy.stdQuote), "01")
        self.assertEquals(self.getRunTimeOutput(source, C=0, quoteFunc=preppy.stdQuote), "12")
        source="{{for i in range(3)}}{{if i==C}}{{continue}}{{endif}}{{i}}{{else}}FORELSE{{endfor}}"
        self.assertEquals(self.getRunTimeOutput(source, C=-1, quoteFunc=preppy.stdQuote), "012FORELSE")
        self.assertEquals(self.getRunTimeOutput(source, C=2, quoteFunc=preppy.stdQuote), "01FORELSE")
        self.assertEquals(self.getRunTimeOutput(source, C=0, quoteFunc=preppy.stdQuote), "12FORELSE")

    fbe_src1="{{for i in range(3)}}{{if i==C}}{{break}}{{endif}}{{i}}{{endfor}}"
    fbe_src2="{{for i in range(3)}}{{if i==C}}{{break}}{{endif}}{{i}}{{else}}FORELSE{{endfor}}"
    def checkForBreakElse1(self):
        self.assertEquals(self.getRunTimeOutput(self.fbe_src1, C=-1, quoteFunc=preppy.stdQuote), "012")

    def checkForBreakElse2(self):
        self.assertEquals(self.getRunTimeOutput(self.fbe_src1, C=2, quoteFunc=preppy.stdQuote), "01")

    def checkForBreakElse3(self):
        self.assertEquals(self.getRunTimeOutput(self.fbe_src1, C=0, quoteFunc=preppy.stdQuote), "")

    def checkForBreakElse4(self):
        self.assertEquals(self.getRunTimeOutput(self.fbe_src2, C=-1, quoteFunc=preppy.stdQuote), "012FORELSE")

    def checkForBreakElse5(self):
        self.assertEquals(self.getRunTimeOutput(self.fbe_src2, C=2, quoteFunc=preppy.stdQuote), "01")

    def checkForBreakElse6(self):
        self.assertEquals(self.getRunTimeOutput(self.fbe_src2, C=0, quoteFunc=preppy.stdQuote), "")

    def checkRaises(self):
        self.assertRaises(ValueError,self.getRunTimeOutput,"{{raise ValueError('aaa')}}")

    trye_src="""TRY{{try}}{{if i==1}}
RAISE{{raise Exception('zzz')}}{{endif}}
TRYBODY{{except}}
EXCEPT{{endtry}}"""
    def checkTryExcept1(self):
        self.assertEquals(self.getRunTimeOutput(self.trye_src, i=0, quoteFunc=preppy.stdQuote), "TRY\nTRYBODY")

    def checkTryExcept2(self):
        self.assertEquals(self.getRunTimeOutput(self.trye_src, i=1, quoteFunc=preppy.stdQuote), "TRY\nRAISE\nEXCEPT")

    tryee_src="""TRY{{try}}{{if i==1}}
raise ValueError{{raise ValueError('bbb')}}{{elif i==2}}
raise TypeError{{raise TypeError('ccc')}}{{elif i==3}}
raise Exception{{raise Exception('zzz')}}{{endif}}{{except ValueError}}
catch ValueError{{except TypeError}}
catch TypeError{{except}}
catch all errors{{else}}
TRYELSE{{finally}}
TRYFINALLY{{endtry}}"""
    def checkTryExceptElseFinally1(self):
        self.assertEquals(self.getRunTimeOutput(self.tryee_src, i=0, quoteFunc=preppy.stdQuote), "TRY\nTRYELSE\nTRYFINALLY")

    def checkTryExceptElseFinally2(self):
        self.assertEquals(self.getRunTimeOutput(self.tryee_src, i=1, quoteFunc=preppy.stdQuote), "TRY\nraise ValueError\ncatch ValueError\nTRYFINALLY")

    def checkTryExceptElseFinally3(self):
        self.assertEquals(self.getRunTimeOutput(self.tryee_src, i=2, quoteFunc=preppy.stdQuote), "TRY\nraise TypeError\ncatch TypeError\nTRYFINALLY")

    def checkTryExceptElseFinally4(self):
        self.assertEquals(self.getRunTimeOutput(self.tryee_src, i=3, quoteFunc=preppy.stdQuote), "TRY\nraise Exception\ncatch all errors\nTRYFINALLY")

    tryf_src="""TRY{{try}}
FTRY{{try}}{{if i==1}}
raise Exception{{raise Exception('zzz')}}{{endif}}
FTRYBODY{{finally}}
FTRYFINALLY{{endtry}}{{except}}
catch all errors{{endtry}}"""
    def checkTryFinally1(self):
        self.assertEquals(self.getRunTimeOutput(self.tryf_src, i=0, quoteFunc=preppy.stdQuote), "TRY\nFTRY\nFTRYBODY\nFTRYFINALLY")

    def checkTryFinally1(self):
        self.assertEquals(self.getRunTimeOutput(self.tryf_src, i=1, quoteFunc=preppy.stdQuote), "TRY\nFTRY\nraise Exception\nFTRYFINALLY\ncatch all errors")

    def checkWith(self):
        fn = preppy.__file__
        self.assertEquals(self.getRunTimeOutput("{{with open(fn,'r') as f}}{{f.name}}{{endwith}}",fn=fn, quoteFunc=preppy.stdQuote),fn)

    def checkImport1(self):
        self.assertEquals(self.getRunTimeOutput('{{import token}}{{token.__name__}}',quoteFunc=preppy.stdQuote),'token')

    def checkImport2(self):
        self.assertEquals(self.getRunTimeOutput('{{import token as x}}{{x.__name__}}',quoteFunc=preppy.stdQuote),'token')

    def checkFrom1(self):
        self.assertEquals(self.getRunTimeOutput('{{from distutils import cmd}}{{cmd.__name__}}',quoteFunc=preppy.stdQuote),'distutils.cmd')

    def checkFrom2(self):
        self.assertEquals(self.getRunTimeOutput('{{from distutils import cmd as x}}{{x.__name__}}',quoteFunc=preppy.stdQuote),'distutils.cmd')

    def checkAssert1(self):
        self.assertRaises(AssertionError,self.getRunTimeOutput,"{{assert i==1}}{{i}}", i=0, quoteFunc=preppy.stdQuote)

    def checkAssert2(self):
        self.assertEquals(self.getRunTimeOutput("{{assert i==1}}{{i}}", i=1, quoteFunc=preppy.stdQuote), "1")

    def checkEmptyScript1(self):
        self.assertEquals(self.getRunTimeOutput('a{{script}}{{endscript}}b',quoteFunc=preppy.stdQuote),'ab')

    def checkEmptyScript2(self):
        self.assertEquals(self.getRunTimeOutput('a{{script}} {{endscript}}b',quoteFunc=preppy.stdQuote),'ab')

    def checkEmptyScript3(self):
        self.assertEquals(self.getRunTimeOutput('a{{script}}\n{{endscript}}b',quoteFunc=preppy.stdQuote),'ab')

    def checkEmptyScript4(self):
        self.assertEquals(self.getRunTimeOutput('a{{script}}\n\n{{endscript}}b',quoteFunc=preppy.stdQuote),'ab')

    def checkEmptyScript5(self):
        self.assertEquals(self.getRunTimeOutput('a{{script}}\n#just a comment{{endscript}}b',quoteFunc=preppy.stdQuote),'ab')

    def checkEmptyScript6(self):
        self.assertEquals(self.getRunTimeOutput('a{{script}}\n#just a comment\n{{endscript}}b',quoteFunc=preppy.stdQuote),'ab')

    def checkEmptyIf1(self):
        self.assertEquals(self.getRunTimeOutput('a{{if False}}{{else}}b{{endif}}c',quoteFunc=preppy.stdQuote),'abc')

    def checkEmptyIf2(self):
        self.assertEquals(self.getRunTimeOutput('a{{if True}}{{else}}b{{endif}}c',quoteFunc=preppy.stdQuote),'ac')

    def checkEmptyIfElse1(self):
        self.assertEquals(self.getRunTimeOutput('a{{if False}}b{{else}}{{endif}}c',quoteFunc=preppy.stdQuote),'ac')

    def checkEmptyIfElse2(self):
        self.assertEquals(self.getRunTimeOutput('a{{if True}}b{{else}}{{endif}}c',quoteFunc=preppy.stdQuote),'abc')

    def checkEmptyWhile1(self):
        self.assertEquals(self.getRunTimeOutput('a{{while False}}{{endwhile}}b',quoteFunc=preppy.stdQuote),'ab')

    def checkEmptyWhile2(self):
        self.assertEquals(self.getRunTimeOutput('{{script}}def I(z=[0,1]):\n return z.pop()\n{{endscript}}a{{while I()}}{{endwhile}}b',quoteFunc=preppy.stdQuote),'ab')

    def checkEmptyWhileElse1(self):
        self.assertEquals(self.getRunTimeOutput('a{{while False}}{{else}}{{endwhile}}b',quoteFunc=preppy.stdQuote),'ab')

    def checkEmptyWhileElse2(self):
        self.assertEquals(self.getRunTimeOutput('{{script}}def I(z=[0,1]):\n return z.pop()\n{{endscript}}a{{while I()}}{{else}}{{endwhile}}b',quoteFunc=preppy.stdQuote),'ab')

    def checkEmptyFor1(self):
        self.assertEquals(self.getRunTimeOutput('a{{for x in ()}}{{endfor}}b',quoteFunc=preppy.stdQuote),'ab')

    def checkEmptyFor2(self):
        self.assertEquals(self.getRunTimeOutput('a{{for x in (0,)}}{{endfor}}b',quoteFunc=preppy.stdQuote),'ab')

    def checkEmptyForElse1(self):
        self.assertEquals(self.getRunTimeOutput('a{{for x in ()}}{{else}}{{endfor}}b',quoteFunc=preppy.stdQuote),'ab')

    def checkEmptyForElse2(self):
        self.assertEquals(self.getRunTimeOutput('a{{for x in (0,)}}{{else}}{{endfor}}b',quoteFunc=preppy.stdQuote),'ab')

    def checkEmptyTry(self):
        self.assertEquals(self.getRunTimeOutput('a{{try}}{{except}}{{else}}{{finally}}{{endtry}}b',quoteFunc=preppy.stdQuote),'ab')

    def checkEmptyWith(self):
        self.assertEquals(self.getRunTimeOutput('a{{with open(fn,'r') as f}}{{endwith}}b',fn=preppy.__file__,quoteFunc=preppy.stdQuote),'ab')

    def checkErrorIndication1(self):
        src = ['line %d' % i for i in range(1000)]
        src = '\n'.join(src + ['{{raise ValueError("AAA")}}'] + src)
        self.assertEquals(checkErrorTextContains('line 1001, in __code__',self.getRunTimeOutput,src,quoteFunc=preppy.stdQuote),'')

    def checkErrorIndication2(self):
        src = ['line %d' % i for i in range(1000)]
        src = '\n'.join(src + ['{{raise ValueError("AAA")}}'])
        self.assertEquals(checkErrorTextContains('line 1001, in __code__',self.getRunTimeOutput,src,quoteFunc=preppy.stdQuote),'')

    def checkErrorIndication3(self):
        src = ['line %d' % i for i in range(1000)]
        src = '\n'.join(['{{raise ValueError("AAA")}}']+src)
        self.assertEquals(checkErrorTextContains('line 1, in __code__',self.getRunTimeOutput,src,quoteFunc=preppy.stdQuote),'')

class NewGeneratedCodeTestCase(unittest.TestCase):
    """Maybe the simplest and most all-encompassing:
    take a little prep file, compile, exec, and verify that
    output is as expected.  This should catch gross failures
    of preppy """

    def getRunTimeOutput(self, prepCode, *args,**kwds):
        "compile code, run with parameters and collect output"
        mod=preppy.getModule('test_preppy',savePyc=0,sourcetext=prepCode)
        return mod.get(*args,**kwds)

    #def checkSpuriousError(self):
    #    self.assertEquals(2+2, 5)


    def checkNoGet(self):
        self.assertRaises(AttributeError,self.getRunTimeOutput,"Hello World")

    def checkUnicodeName(self):
        mod=preppy.getModule(u'./test_preppy',savePyc=0,sourcetext='Hello World')

    def checkUnicodeDirectory(self):
        mod=preppy.getModule('./test_preppy',directory=u'.',savePyc=0,sourcetext='Hello World')

    def checkUnicodeExtension(self):
        mod=preppy.getModule('./test_preppy',source_extension=u'.prep',savePyc=0,sourcetext='Hello World')

    def checkUnicodeSourceText(self):
        mod=preppy.getModule('./test_preppy',savePyc=0,sourcetext=u'Hello World')

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
        output1 = ''.join(collector)
        from preppy import StringIO
        buf = StringIO()
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
              'inner':modInner}
        output = modOuter.getOutput(ns)
        #self.assertRaises(NameError, modOuter.getOutput, ns)
        self.assertEquals(output, "NORTHSOUTHEASTWEST")

    def testIncludeQuoting(self):
        m = preppy.getModule('outer',savePyc=0)
        self.assertEquals(m.getOutput(dict(j='J')),
                'in outer.prep\n\n\tbefore include inner i=0 j=J\n\tin inner.prep v=J*10 w=0\n\n\tbefore include inner1 i=0 j=J\n\tin inner1.prep v=0 w=J*100\n\n\tafter include inner1 i=0 j=J\n\n')
        self.assertEquals(m.getOutput(dict(j='J'),quoteFunc=lambda x: '[%s]' % x),
                'in outer.prep\n\n\tbefore include inner i=[0] j=[J]\n\t[[in inner.prep v=][J*10][ w=][0][\n]]\n\tbefore include inner1 i=[0] j=[J]\n\t[in inner1.prep v=[0] w=[J*100]\n]\n\tafter include inner1 i=[0] j=[J]\n\n')

def makeSuite():
    suite1 = unittest.makeSuite(NewGeneratedCodeTestCase,'check')
    suite2 = unittest.makeSuite(GeneratedCodeTestCase,'check')
    suite3 = unittest.makeSuite(OutputModeTestCase,'check')
    suite4 = unittest.makeSuite(IncludeTestCase)
    return unittest.TestSuite((suite1,suite2, suite3, suite4))

if __name__=='__main__':
    runner = unittest.TextTestRunner()
    runner.run(makeSuite())
