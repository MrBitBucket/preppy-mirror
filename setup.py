try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
import os, sys, glob

if __name__=='__main__':
    pkgDir=os.path.dirname(sys.argv[0])
    if not pkgDir:
        pkgDir=os.getcwd()
    if not os.path.isabs(pkgDir):
        pkgDir=os.path.abspath(pkgDir)
    sys.path.insert(0,pkgDir)
    os.chdir(pkgDir)
    if len(sys.argv)>=2 and sys.argv[1]=='test':
        import subprocess
        def spCall(cmd,*args,**kwds):
            r = subprocess.call(
                    cmd,
                    stderr = subprocess.STDOUT,
                    stdout = subprocess.DEVNULL if kwds.pop('dropOutput',False) else None,
                    timeout = kwds.pop('timeout',3600),
                    )
            if False:
                pfx = '!!!!!' if r else '#####'
                scmd = ' '.join(cmd)
                print(f'{pfx} {scmd} --> {r}')
            return r
        def specialOption(n,ceq=False):
            v = 0
            while n in sys.argv:
                v += 1
                sys.argv.remove(n)
            if ceq:
                n += '='
                V = [_ for _ in sys.argv if _.startswith(n)]
                for _ in V: sys.argv.remove(_)
                if V:
                    n = len(n)
                    v = V[-1][n:]
            return v
        failfast = specialOption('--failfast')
        verboseTests = specialOption('--verbose-tests')
        excludes = [_ for _ in sys.argv if _.startswith('--exclude=')]
        for _ in excludes:
            sys.argv.remove(_)
        if len(sys.argv)!=2:
            raise ValueError('test may only be used alone sys.argv[1:]=%s' % repr(sys.argv[1:]))
        cmd = sys.argv[-1]
        os.chdir(os.path.join(pkgDir,'test'))
        cli = [sys.executable, 'testall.py']+excludes
        if verboseTests:
            cli.append('--verbosity=2')
        if failfast:
            cli.append('--failfast')
        r = spCall(cli)
        sys.exit(f'!!!!! testall.py --> {r} !!!!!' if r else r)

    import preppy
    version = preppy.VERSION

    setup(name='preppy',
        version=version,
        license="BSD license (see license.txt for details), Copyright (c) 2000-2022, ReportLab Inc.",
        license_files=('LICENCE.txt',),
        classifiers = [
            'Development Status :: 5 - Production/Stable',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: BSD License',
            'Topic :: Printing',
            'Topic :: Text Processing :: Markup',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.7',
            'Programming Language :: Python :: 3.8',
            'Programming Language :: Python :: 3.9',
            'Programming Language :: Python :: 3.10',
            'Programming Language :: Python :: 3.11',
            'Programming Language :: Python :: 3.12',
            'Programming Language :: Python :: 3.13',
            ],
        description='preppy - a Preprocessor for Python',
        long_description='preppy - a Preprocessor for Python. See https://preppy.readthedocs.io/',
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
    if 'bdist_wheel' in sys.argv:
        bfn = f'preppy-{version}-py3-none-any.whl'
        renamed = False
        if '--dist-dir' in sys.argv:
            distDir = sys.argv[sys.argv.index('--dist-dir')+1]
            fn = glob.glob(os.path.join(distDir,bfn))
            if len(fn)==1:
                fn = fn[0]
                nfn = fn.replace('-py3-','-py2.py3-')
                if os.path.isfile(nfn): os.remove(nfn)
                os.rename(fn, nfn)
                print(f'##### {bfn} was renamed to {os.path.basename(nfn)} #####')
                renamed = True
        if not renamed:
            print(f'!!!!! {bfn} not renamed !!!!!')
