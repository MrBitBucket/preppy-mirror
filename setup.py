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
