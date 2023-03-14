try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
import os, sys

if __name__=='__main__':
    pkgDir=os.path.dirname(sys.argv[0])
    if not pkgDir:
        pkgDir=os.getcwd()
    if not os.path.isabs(pkgDir):
        pkgDir=os.path.abspath(pkgDir)
    sys.path.insert(0,pkgDir)
    os.chdir(pkgDir)

    import preppy
    version = preppy.VERSION

    setup(name='preppy',
        version=version,
        description='preppy - a Preprocessor for Python',
        author='Robin Becker, Andy Robinson, Aaron Watters',
        author_email='andy@reportlab.com',
        url='https://hg.reportlab.com/hg-public/preppy',
        py_modules=['preppy'],
        entry_points = dict(
                        console_scripts = [
                                'preppy=preppy:main',
                                ],
                            ),
        )
