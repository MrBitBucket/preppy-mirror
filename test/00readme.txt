Execute check_basics.py.  This requires
PyUnit's unittest.py which is in reportlab.test.


John Precedo 17:11 09/11/2000

Run interactivly:
>>> len( {'a':  {'b':'c'}} )  
1

In a test program:
This should contain the digit '1':  {{len({ 'a':  {'b':'c'}$})   }}  


This gives:
Run: 5 Failures: 0 Errors: 1
There was 1 error:
1) __main__.SimpleTestCase.check5Escape
Traceback (innermost last):
  File "C:\john\rlextra\preppy\test\CHECK_~1.PY", line 21, in check5Escape
    processTest('sample005')
  File "C:\john\rlextra\preppy\test\CHECK_~1.PY", line 30, in processTest
    mod.run(dictionary, outputfile = outFile)
  File "<string>", line 88, in run
KeyError: len#[# 

