#Copyright ReportLab Europe Ltd. 2000-2021
#see license.txt for license details

## new style calling
def run():
    from preppy import getModule
    import os
    module = getModule(os.path.join(os.path.dirname(__file__),"newstyle.prep"), verbose=1)
    print(module.get([('fred', 'm'),('bill','f'),('bacterium','other'),('jill','m')],
                            __quoteFunc__=str, __lquoteFunc__=str))

if __name__=='__main__':
    run()
