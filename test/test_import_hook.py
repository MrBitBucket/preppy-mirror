import os, sys, unittest
import preppy
from check_basics import fposto

class ImportTestCase(unittest.TestCase):
    def setUp(self):
        self.cwd = os.getcwd()
        dn = os.path.dirname(sys.argv[0])
        if dn: os.chdir(dn)
        preppy.installImporter()

    @fposto
    def testImport1(self):
        if os.path.isfile('sample001.pyc'):
            os.remove('sample001.pyc')
        import sample001
        sample001.getOutput({})

        #uninstallImporter seems not to work

    @fposto
    def testImport2(self):
        if os.path.isfile('sample001n.pyc'):
            os.remove('sample001n.pyc')
        import sample001n
        sample001n.get(A=4)

    @fposto
    def testImport3(self):
        parentDir = os.path.normpath(os.path.join(os.getcwd(),'..'))
        sys.path.insert(0,parentDir)
        try:
            for name in 'sample001 sample001n'.split():
                if name in sys.modules:
                    del sys.modules[name]
            import test.sample001, test.sample001n
        finally:
            sys.path.remove(parentDir)

    def tearDown(self):
        preppy.uninstallImporter()
        if self.cwd!=os.getcwd():
            os.chdir(self.cwd)

class PythonImportTestCase(unittest.TestCase):
    def setUp(self):
        self.cwd = os.getcwd()
        dn = os.path.dirname(sys.argv[0])
        if dn: os.chdir(dn)

    @fposto
    def testPythonImport1(self):
        self.assertTrue(os.path.isfile('sample001.pyc'))
        if 'sample001' in sys.modules:
            del sys.modules['sample001']
        import sample001
        sample001.getOutput({})

    @fposto
    def testPythonImport2(self):
        self.assertTrue(os.path.isfile('sample001n.pyc'))
        if 'sample001n' in sys.modules:
            del sys.modules['sample001n']
        import sample001n
        sample001n.get(A=4)

    def tearDown(self):
        preppy.uninstallImporter()
        if self.cwd!=os.getcwd():
            os.chdir(self.cwd)

def makeSuite():
    suite = unittest.makeSuite(ImportTestCase)
    suite.addTests(unittest.makeSuite(PythonImportTestCase))
    return suite

if __name__=='__main__':
    runner = unittest.TextTestRunner()
    runner.run(makeSuite())
