#
import os
import preppy
import unittest

class ImportTestCase(unittest.TestCase):

        

    def testHook(self):
        preppy.installImporter()
        if os.path.isfile('sample001.pyc'):
            os.remove('sample001.pyc')
        import sample001
        sample001.getOutput({})

        #uninstallImporter seems not to work

        

def makeSuite():        
    return unittest.makeSuite(ImportTestCase)


if __name__=='__main__':
    runner = unittest.TextTestRunner()
    runner.run(makeSuite())
