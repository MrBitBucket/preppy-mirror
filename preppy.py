"""Python preprocessor"""

STARTTAG = "${"
ENDTAG = "$}"

VERSION = 0.1

"""
${if x:$} this text $(endif$} that

becomes

if x:
    print (" this text"),
print (that\n")

note that extra spaces may be introduced compliments of print.
could change this to a file.write for more exact control...
"""

import string

KEYWORDS = string.split("""
    if else elif for while script
    endif endfor endwhile
""")

def printstmt(txt, newline=1, linemax=40):
    """UNCLOSED call to __write__ 
       if everything is properly quoted you can append a % (x1, x2, x3)) onto the end of this"""
    lines = string.split(txt, "\n")
    out = []
    a = out.append
    start = 1
    while lines:
        l = lines[0]
        del lines[0]
        while l:
            l1 = l[:linemax]
            l = l[linemax:]
            if not l and lines:
                # paste back the newline
                l1 = l1+"\n"
            if start:
                a("__write__ (  (%s" % repr(l1))
                start = 0
            else:
                a("\t %s" % repr(l1))
    if not out:
        return "" # no write!
    last = out[-1]
    if newline:
        final = ")"
    else:
        final = "),"
    out[-1] = last + " )"
    return string.join(out, "\n")

def quotestring(s, cursor=0):
    """return a string where ${x$} becomes %(x)s and % becomes %(__percent__)s
       and also return a substitution dictionary for it containing
          __dict__ = {}
          __dict__["__percent__"] = "%"
          ...
          __dict__["x"] = x
          ...
       return the cursor where the process breaks (end or at ${if x:...}
       ${x$} x must not contain whitespace (except surrounding) but it can be (eg)
       math.sin(34.1) or dictionary.get("user","anonymous")
    """
    #print "quotestring at", cursor, repr(s[cursor:cursor+10])
    from string import join, split, strip, find, replace
    slen = len(s)
    quotedparts = []
    addpart = quotedparts.append
    dictlines = ["__dict__ = {}"]
    adddict = dictlines.append
    done = None
    starttaglen = len(STARTTAG)
    endtaglen = len(ENDTAG)
    dictassntemplate = "__dict__[%s] = %s # %s"
    while done is None:
        findpercent = find(s, "%", cursor)
        if findpercent<0: findpercent = slen
        findstarttag = find(s, STARTTAG, cursor)
        if findstarttag<0: findstarttag = slen
        findmin = min(findpercent, findstarttag)
        sclean = s[cursor:findmin]
        addpart(sclean)
        #print "clean", repr(sclean)
        cursor = findmin
        if cursor==slen:
            done = 1
        elif s[cursor]=="%":
            cursor = cursor+1
            addpart("%(#percent#)s")
        else:
            # must be at start tag
            findendtag = find(s, ENDTAG, cursor)
            savecursor = cursor
            cursor = cursor+starttaglen
            if findendtag<0:
                raise ValueError, "no end tag found after %s" % repr(s[cursor-10:cursor+20])
            block = s[cursor: findendtag]
            block = strip(block)
            if block[-1]==":":
                blockx = block[:-1]
            else:
                blockx = split(block)[0]
            if complexdirective(block) or blockx in KEYWORDS:
                cursor = savecursor
                done = 1 # can't handle more complex things here
            else:
                cursor = findendtag+endtaglen
                sblock = block
                # quote for substitution format
                for (c, rc) in (("%", "#P#"), ("(", "#[#"), (")", "#]#")):
                    if c in sblock:
                        sblock = replace(sblock, c, rc)
                substitutionline = dictassntemplate % (repr(sblock), block, repr(s[savecursor:cursor+10]))
                adddict(substitutionline)
                stringsub = "%s(%s)s" % ("%", sblock)
                addpart(stringsub)
    percentline = dictassntemplate % (repr("#percent#"), repr("%"), "required percent sub")
    adddict(percentline)            
    quotestring = join(quotedparts, "")
    dictstring = join(dictlines, "\n")
    #print "==== dictstring"
    #print dictstring
    #print "==== quotestring"
    #print quotestring
    return (quotestring, dictstring, cursor)

teststring = """
this test script should produce a runnable program
${script
  class X:
      pass
  x = X()
  x.a = "THE A VALUE OF X"
  yislonger = "y is longer!"
  import math
  a = dictionary = {"key": "value", "key2": "value2", "10%": "TEN PERCENT"}
  loop = "LOOP"
$}
this line has a percent in it 10%
here is the a value in x: ${x.a$}
just a norml value here: ${yislonger$} string ${a["10%"]$}
 the sine of 12.3 is ${math.sin(12.3)$}
 ${script a=0$}
 these parens should be empty
 (${if a:$}
conditional text${endif$})
 ${script a=1$}
 these parens should be full
 (${if a:$}
conditional text${endif$})
stuff between endif and while

${while a==1:$} infinite ${loop$} forever!
${script a=0$}
${for (a,b) in dictionary.items():$}
the key in the dictionary is ${a$} and the value is ${b$}.  And below is a script
${script
        # THIS IS A SCRIPT
        x = 2
        y = 3
        # END OF THE SCRIPT
$}
stuff after the script
${endfor$}
stuff after the for stmt
${endwhile$}
stuff after the while stmt
"""

"""
# test code for quotestring
(qs, ds, c) = quotestring(teststring, cursor=0)
print "---------quoted to ", c, `teststring[c:c+20]`
print qs
print "---------dict string"
print ds
"""

class PreProcessor:
    STARTTAG = STARTTAG
    ENDTAG = ENDTAG
    indentstring = "\t"
    def indent(self, s):
        indentstring = self.indentstring
        return indentstring + string.replace(s, "\n", "\n"+indentstring)
    
    def __call__(self, inputtext, cursor=0, toplevel=1):
        # go to end of string (if toplevel) or dedent token (if not toplevel)
        #print "call at", cursor, repr(inputtext[cursor:cursor+10])
        if toplevel:
            outputlist = ["import sys", "__write__=sys.stdout.write"]
        else:
            outputlist = []
        a = outputlist.append
        #def a(s, outputlist=outputlist):
        #    "debug version"
        #    print "    ===== adding"
        #    print s
        #    outputlist.append(s)
        from string import strip, join, find
        done = None
        inputlen = len(inputtext)
        while done is None:
            # do a print statement for stuff before a complex directive
            #print "iterating at", cursor, repr(inputtext[cursor:cursor+10])
            (quoted, dictstring, newcursor) = quotestring(inputtext, cursor)
            if "%" in quoted:
                a(dictstring)
                prints = printstmt(quoted) + "% __dict__ )" # note comma!
            else:
                segment = inputtext[cursor: newcursor]
                prints = printstmt(segment)
                if prints:
                    # close it
                    prints = prints + ")"
            a(prints)
            cursor = newcursor
            if cursor>=inputlen:
                done = 1
            else:
                # should be at a complex directive
                (startblock, block, sblock, newcursor) = self.getDirectiveBlock(cursor, inputtext)
                if newcursor==cursor:
                    raise ValueError, "no progress in getdirectiveblock"
                oldcursor = cursor
                cursor = newcursor
                # now test for constructs
                if find(sblock, "if") == 0:
                    #print "in if"
                    # if statement, first add the block line
                    a(sblock)
                    # then get the conditional block
                    (conditional, cursor) = self(inputtext, cursor, toplevel=0)
                    iconditional = self.indent(conditional)
                    a(iconditional)
                    inif = 1
                    while inif:
                        # now we should be at an else elif or endif
                        if find(inputtext, STARTTAG, cursor)!=cursor:
                            raise ValueError, "not at starttag"
                        (startblock, block, sblock, cursor) = self.getDirectiveBlock(cursor, inputtext)
                        if find(sblock, "else")==0:
                            if complexdirective(block):
                                raise ValueError, "bad else? %s" %repr(sblock)
                            a(sblock)
                            (conditional, cursor) = self(inputtext, cursor, toplevel=0)
                            iconditional = self.indent(conditional)
                            a(iconditional)
                            # MUST be at endif
                            inif = 0
                            (startblock, block, sblock, cursor) = self.getDirectiveBlock(cursor, inputtext)
                            if find(sblock, "endif")!=0:
                                raise ValueError, "else not followed by endif %s.%s" % (
                                    repr(inputtext[startblock-10:startblock]), repr(inputtext[startblock:startblock+10]))
                            if complexdirective(block):
                                raise ValueError, "bad endif? %s" %repr(sblock)
                        elif find(sblock, "elif")==0:
                            a(sblock)
                            (conditional, cursor) = self(inputtext, cursor, toplevel=0)
                            iconditional = self.indent(conditional)
                            a(iconditional)
                        elif find(sblock, "endif")==0:
                            #print "saw endif"
                            inif = 0
                elif find(sblock, "while") == 0 or find(sblock, "for")==0:
                    if find(sblock, "while") == 0: directive="while"
                    elif find(sblock, "for")==0: directive="for"
                    #print "in", directive
                    # while statement
                    a(sblock)
                    # then get the conditional block
                    (conditional, cursor) = self(inputtext, cursor, toplevel=0)
                    iconditional = self.indent(conditional)
                    a(iconditional)
                    (startblock, block, sblock, cursor) = self.getDirectiveBlock(cursor, inputtext)
                    if find(sblock, "end"+directive)!=0:
                        raise ValueError, "%s not followed by end%s %s.%s" % (directive, directive,
                            repr(inputtext[startblock-10:startblock]), repr(inputtext[startblock:startblock+10]))
                    if complexdirective(block):
                        raise ValueError, "bad end marker? %s" %repr(block)
                    #print "... done with", directive
                elif find(sblock, "script")==0:
                    # include literal code, indented properly
                    # strip out script tag
                    fscript = find(block, "script")
                    ddblock = block[fscript+len("script"):]
                    ddblock = dedent(ddblock)
                    #print "... dedented script"
                    #print ddblock
                    a(ddblock)
                elif not toplevel:
                    # assume the calling routine understands the directive
                    #print "defaulting to return"
                    cursor = oldcursor
                    done = 1
                    continue
                else:
                    raise ValueError, "at toplevel don't understand directive %s.%s" % (
                        repr(inputtext[startblock-10:startblock]), repr(inputtext[startblock:startblock+10]))
        output = join(outputlist, "\n")
        return (output, cursor)
    
    def getDirectiveBlock(self, cursor, inputtext):
        #print repr((inputtext[cursor], inputtext[cursor:cursor+20]))
        from string import find, strip
        starttaglen = len(STARTTAG)
        endtaglen = len(ENDTAG)
        # should be at a starttag
        newcursor = cursor+starttaglen
        if inputtext[cursor:newcursor]!=STARTTAG:
                    raise ValueError, "no start tag found at %s.%s" % (
                        repr(inputtext[cursor-10:cursor]), repr(inputtext[cursor:cursor+10]))
        cursor = newcursor
        findendtag = find(inputtext, ENDTAG, cursor)
        if findendtag<cursor:
                    raise ValueError, "no end tag found after %s.%s" % (
                        repr(inputtext[cursor-10:cursor]), repr(inputtext[cursor:cursor+10]))
        startblock = cursor
        endblock = findendtag
        block = inputtext[startblock:endblock]
        cursor = endblock+endtaglen
        sblock = strip(block)
        return (startblock, block, sblock, cursor)

    def module_source(self, string):
        """make a module with a function run(dictionary) which executes the interpreted string"""
        (out, c) = self(string)
        iout = self.indent(out)
        result = module_source_template % iout
        return result

def complexdirective(s):
    from string import split, strip
    return len(split(strip(s))) != 1

def dedent(text):
    """get rid of redundant indentation in text
       this dedenter IS NOT smart about converting tabs to spaces!!!"""
    from string import split, find, strip, join
    lines = split(text, "\n")
    # omit empty lines
    while lines and not strip(lines[0]):
        del lines[0]
    if not lines:
        return "" # completely white
    line0 = lines[0]
    sline0 = strip(line0)
    ssline0 = split(sline0)
    firstword = ssline0[0]
    findfirstword = find(line0, firstword)
    if findfirstword<0:
        raise "huh?"
    indent = line0[:findfirstword]
    linesout = []
    for l in lines:
        if not strip(l):
            linesout.append("")
            continue
        lindent = l[:findfirstword]
        if lindent!=indent:
            raise ValueError, "inconsistent indent expected %s got %s in %s" % (repr(indent), repr(lindent), l)
        linesout.append(l[findfirstword:])
    return join(linesout, "\n")

module_source_template = """
def run(dictionary):
%s

if __name__=="__main__":
    run({})
"""

def parsetest():        
    fn = "./testoutput.py"
    P = PreProcessor()
    (out, c) = P(teststring)
    print "generated", len(out), "bytes from", c, "input"
    print "generating file", fn
    f = open(fn, "w")
    import sys
    stdout = sys.stdout
    sys.stdout = f
    print out
    sys.stdout = stdout
    print "wrote", fn

def testgetmodule():
    name = "testpreppy"
    print "trying to load", name
    result = getPreppyModule(name, verbose=1)
    print "load successful! running result"
    print "=" * 100
    result.run({})

def getPreppyModule(name, directory=".", source_extension=".prep", verbose=0):
    # see if the module exists as a python file
    from sys import path
    import os
    sourcefilename = os.path.join(directory, name+source_extension)
    if directory not in path:
        path.insert(0, directory)
    try:
        module = __import__(name)
        checksum = module.__checksum__
        if verbose: print "module", name, "found with checksum", repr(checksum)
    except ImportError:
        module = checksum = None
        if verbose: print "no module", name, "found"
    # check against source file
    try:
        sourcefile = open(sourcefilename, "r")
    except:
        if verbose: print "no source file", sourcefilename, "found attempting to use existing module"
        if module is None:
            raise ValueError, "couldn't find source %s or module %s" % (sourcefilename, name)
        # use the existing module??? (NO SOURCE PRESENT)
        return module
    else:
        sourcetext = sourcefile.read()
        import md5
        # NOTE: force recompile on each new version of this module.
        sourcechecksum = md5.new(sourcetext + repr(VERSION)).digest()
        if sourcechecksum==checksum:
            # use the existing module. it matches
            if verbose: print "checksums match, not regenerating python source"
            return module
        elif verbose:
            print "CHECKSUMS DON'T MATCH"
    # if we got here we need to rebuild the module from source
    if verbose:
        print "regenerating python source from", sourcefilename
    P = PreProcessor()
    out = P.module_source(sourcetext)
    outfilename = os.path.join(directory, name+".py")
    outfile = open(outfilename, "w")
    outfile.write("""
'''
PREPPY MODULE %s
Automatically generated file from preprocessor source %s
DO NOT EDIT!
'''
__checksum__ = %s
""" % (name, sourcefilename, repr(sourcechecksum)))
    outfile.write(out)
    outfile.close()
    # now make a module
    from imp import new_module
    result = new_module(name)
    exec out in result.__dict__
    return result

if __name__=="__main__":
    parsetest()
    print; print "PAUSING.  To continue hit return"
    raw_input("now: ")
    testgetmodule()
    
                