#Copyright ReportLab Europe Ltd. 2000-2021
#see license.txt for license details

## new style calling
def run():
    from preppy import getModule
    module = getModule("newstyle.prep", verbose=1)
    print(module.get([('fred', 'm'),('bill','f'),('bacterium','other'),('jill','m')]))

if __name__=='__main__':
    run()
    
