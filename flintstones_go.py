#copyright ReportLab Inc. 2000
#see license.txt for license details
#history www.reportlab.co.uk/rl-cgi/viewcvs.cgi/rlextra/preppy/flintstones_go.py
#$Header: /rl_home/xxx/repository/rlextra/preppy/flintstones_go.py,v 1.7 2002/04/10 00:31:36 andy Exp $

## exerciser test module for preppy.
def run():
    from os import unlink
    name = "flintstone"
    for fn in (name+".py", name+".pyc"):
        try:
                unlink(fn)
                print "deleted", fn
        except:
                print "no", fn, "to delete"
    from preppy import getModule
    result = getModule(name, verbose=1)
    print "="*77
    D =  {'sex': 'm', 'name': 'george', "invalid variable name": 45}
    # tricky security holes like this are sealed...
    D["""__d__[__import__("sys").stdout.write("ThisAintAllowed")]"""] = 90
    import sys
    # don't do this
    #result.run(D, __write__=sys.stdout.write, outputfile=open("flintstone.html", "w"))

    # do this
    hname = name+".html"
    print "generating", hname
    result.run(D, outputfile=open(hname, "w"))


    print "="*77
    # or this
    print "now generating to stdout"
    result.run(D, __write__=sys.stdout.write)

    # or this (default to __write__ = sys.stdout.write)
    #result.run(D)

    print "*"*66

    print "now testing memory to memory option"

    text = open("flintstone.prep", "r").read()
    result = getModule("flintstone2", sourcetext=text, verbose=1)
    print "="*55
    result.run(D)

if __name__=='__main__':
    run()
    