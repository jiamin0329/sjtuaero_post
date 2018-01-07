#!/usr/local/bin/python
#######################################################
#            File Describtion
#######################################################
#  This class is implemented for utilities for CFD++.
# 
#######################################################
#  Date          Author           Description
#  07-Jan-2018   Jiamin Xu        Creation
#######################################################
#            Import Modules
#######################################################
import os

#######################################################
#            Global Variables
#######################################################


#######################################################
#            Classes or Functions
#######################################################
def CreateCGNSFile(caseName, cgnsFile = "solution.cgns"):
    """Create cgns file"""
    if not os.path.exists(caseName):
        print("Case not found --- " + caseName)

    try:
        ret = os.chdir(caseName)
        if not os.path.exists("pltosout.bin"):
            print("File not found --- pltosout.bin")

        logFile = "convertToCgns.log"
        convertToCgns = "converttoCGNS " + cgnsFile + " 1 1 > "  + logFile
        print("Creating cgns file...")
        ret = os.system(convertToCgns)
        ret = os.chdir("..")

    except Exception as e:
        print(e)
        exit(1)
        
    else:
        print ("CGNS file is created!")
               
#######################################################
#            Main Function
#######################################################
if __name__ == '__main__':
    CreateCGNSFile("sample")

    pass
