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
result.run(D)