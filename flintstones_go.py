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
D =  {'sex': 'm', 'name': 'george'}
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
