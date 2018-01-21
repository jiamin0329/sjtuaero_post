#!/usr/local/bin/python
#######################################################
#            File Describtion
#######################################################
#  This class is implemented for tecplot mcr commands.
#
#  1. WriterMcrHeader
#  2. WriteMcrLoadCgnsFile
#  3. WriteMcrCloseTec360
#  4. WriteMcrPressureCoeff
#  5. WriteMcrOutputContour
#  6. WriteMcrOutputVarDistribution
# 
#######################################################
#  Date          Author           Description
#  02-Nov-2017   Jiamin Xu        Creation
#  12-Nov-2017   Jiamin Xu        Handle spanwise load
#  17-Nov-2017   Jiamin Xu        Handle wing root blending moment
#  21-Jan-2018   Jiamin Xu        Refactor all methods
#######################################################
#            Import Modules
#######################################################
import os
import shutil

#######################################################
#            Global Variables
#######################################################


#######################################################
#            Classes or Functions
#######################################################
def WriteMcrHeader(tecplotPath):
    ## MCR COMMANDs: MCR header texts
    mcrText = []
    mcrText.append("#!MC 1410\n")
    mcrText.append("$!VarSet |MFBD| = \'" + tecplotPath + "\'\n")
    mcrText.append("####################################################\n")
    mcrText.append("## This tecplot mcr file is produced automatically.\n")
    mcrText.append("## DON'T do any modification.\n")
    mcrText.append("####################################################\n")
    return mcrText

    
def WriteMcrLoadCgnsFile(cgnsFile):
    ## MCR COMMANDs: load solution cgns file into tecplot
    mcrText = []
    mcrText.append("####################################################\n")
    mcrText.append("## Load Solution File\n")
    mcrText.append("####################################################\n")
    mcrText.append("$!READDATASET  '" + "\"STANDARDSYNTAX\" \"1.0\" \"FILELIST_CGNSFILES\" \"1\" " + "\"" + cgnsFile + "\" " + "\"LoadBCs\" \"Yes\" \"AssignStrandIDs\" \"Yes\" \"LoaderVersion\" \"V3\" \"CgnsLibraryVersion\" \"3.1.4\"'\n")
    mcrText.append("  DATASETREADER = 'CGNS Loader'\n")
    mcrText.append("  READDATAOPTION = NEW\n")
    mcrText.append("  RESETSTYLE = YES\n")
    mcrText.append("  ASSIGNSTRANDIDS = NO\n")
    mcrText.append("  INITIALPLOTTYPE = CARTESIAN3D\n")
    mcrText.append("  INITIALPLOTFIRSTZONEONLY = NO\n")
    mcrText.append("  ADDZONESTOEXISTINGSTRANDS = NO\n")
    mcrText.append("$!RemoveVar |MFBD|\n")
    mcrText.append("####################################################\n\n")
    return mcrText

    
def WriteMcrCloseTec360():
    ## MCR COMMANDs: close tec360
    mcrText = []
    mcrText.append("#######################################\n")
    mcrText.append("## Quit Tec360\n")
    mcrText.append("$!QUIT")
    return mcrText


def WritePressureCoeff(refPres, refDens, refVmag, indPres):
    ## MCR COMMANDs: setup pressure coefficient
    mcrText = []
    mcrText.append("####################################################\n")
    mcrText.append("## Setup Pressure Coefficient\n")
    mcrText.append("####################################################\n")
    mcrText.append("$!ALTERDATA\n")
    eq_cp = '(V' + str(indPres) + '-' + str(refPres) + ')/(0.5*' + str(refDens) + '*' + str(refVmag) + '*' + str(refVmag) + ')'
    mcrText.append("  EQUATION = '{Cp}=" + eq_cp + "'\n")
    mcrText.append("####################################################\n")
    return mcrText


def WriteMcrOutputContour(numZones, surfZones, varIndex, levels, viewType = "+Y view", outputFile = "output.jpg"):
    ## MCR COMMANDs: output pressure contours
    mcrText = []
    mcrText.append("#######################################\n")
    mcrText.append("## Output Pressure Contour\n")
    mcrText.append("#######################################\n")
    ## MCR COMMANDs: turn off showshade and light effect
    mcrText.append("$!FIELDLAYERS SHOWSHADE = NO\n")
    mcrText.append("$!FIELDLAYERS USELIGHTINGEFFECT = NO\n")
    ## MCR COMMANDs: switch on surface zones ONLY
    for i in range(numZones):
        mcrText.append("$!ACTIVEFIELDMAPS -= [" + str(i+1) + "]\n")

    for i in surfZones:
        mcrText.append("$!ACTIVEFIELDMAPS += [" + str(i) + "]\n")

    mcrText.append("$!GLOBALRGB REDCHANNELVAR = 9\n")
    mcrText.append("$!GLOBALRGB GREENCHANNELVAR = 4\n")
    mcrText.append("$!GLOBALRGB BLUECHANNELVAR = 4\n")

    mcrText.append("$!SETCONTOURVAR\n")
    mcrText.append("  VAR = " + str(varIndex) + "\n")
    mcrText.append("  CONTOURGROUP = 1\n")
    mcrText.append("  LEVELINITMODE = RESETTONICE\n")
  
    mcrText.append("$!FIELDLAYERS SHOWCONTOUR = YES\n")
    mcrText.append("$!CONTOURLEVELS NEW\n")
    mcrText.append("  CONTOURGROUP = 1\n")
    mcrText.append("  RAWDATA\n")

    numLevels = len(levels)
    mcrText.append(str(numLevels) + "\n")

    for level in levels:
        mcrText.append(str(level) + "\n")

    allSurfZones = str(surfZones[0]) + "-" + str(surfZones[-1])
    mcrText.append("$!FIELDMAP [" + allSurfZones + "]  CONTOUR{CONTOURTYPE = BOTHLINESANDFLOOD}")

    psiAngle   = 0.0
    thetaAngle = 0.0
    alphaAngle = 0.0
    if   viewType == "+X view":
        psiAngle   =   90.0
        thetaAngle =  -90.0
        alphaAngle =    0.0
    elif viewType == "-X view":
        psiAngle   =    0.0
        thetaAngle =   90.0
        alphaAngle =    0.0
    elif viewType == "+Y view":
        psiAngle   =   90.0
        thetaAngle =  180.0
        alphaAngle =    0.0
    elif viewType == "-Y view":
        psiAngle   =   90.0
        thetaAngle =    0.0
        alphaAngle =    0.0
    elif viewType == "+Z view":
        psiAngle   =    0.0
        thetaAngle =    0.0
        alphaAngle =    0.0
    elif viewType == "-Z view":
        psiAngle   =  180.0
        thetaAngle = -180.0
        alphaAngle =    0.0

    mcrText.append("## fit data to the view\n")
    mcrText.append("$!THREEDVIEW PSIANGLE = "   + str(psiAngle)   + "\n")
    mcrText.append("$!THREEDVIEW THETAANGLE = " + str(thetaAngle) + "\n")
    mcrText.append("$!THREEDVIEW ALPHAANGLE = " + str(alphaAngle) + "\n")
    mcrText.append("$!VIEW FITSURFACES\n")
    
    mcrText.append("## export frame\n")
    mcrText.append("$!EXPORTSETUP EXPORTFORMAT = JPEG\n")
    mcrText.append("$!EXPORTSETUP IMAGEWIDTH = 1045\n")
    mcrText.append("$!EXPORTSETUP QUALITY = 100\n")
    mcrText.append("$!EXPORTSETUP JPEGENCODING = PROGRESSIVE\n")
    mcrText.append("$!EXPORTSETUP EXPORTFNAME = '" + outputFile + "'\n")
    mcrText.append("$!EXPORT\n") 
    mcrText.append("  EXPORTREGION = CURRENTFRAME\n")
    
    mcrText.append("#######################################\n\n")
    return mcrText


def WriteMcrVarDistribution(section, zoneIndex, varIndex, slicePlane = "YPLANES", outputFile = "output.dat"):
    mcrText = []
    mcrText.append("#######################################\n")
    mcrText.append("## Variable Distribution at section " + str(section) + "\n")
    mcrText.append("#######################################\n")
    mcrText.append("## add slice\n")
    mcrText.append("$!SLICEATTRIBUTES 1  EDGELAYER{SHOW = YES}\n")
    mcrText.append("$!SLICEATTRIBUTES 1  SLICESOURCE = SURFACEZONES\n")
    mcrText.append("$!SLICELAYERS SHOW = YES\n")

    mcrText.append("$!SLICEATTRIBUTES 1  SLICESURFACE =" + slicePlane + "\n")
    mcrText.append("$!SLICEATTRIBUTES 1  PRIMARYPOSITION{Y = " + str(section) + "}\n")
    mcrText.append("## extract slice data\n")
    mcrText.append("$!CREATESLICEZONES\n")
    mcrText.append("## write slice data\n")
    mcrText.append("$!WRITEDATASET  \"" + outputFile + "\"\n")
    mcrText.append("  INCLUDETEXT = NO\n")
    mcrText.append("  INCLUDEGEOM = NO\n")
    mcrText.append("  INCLUDEDATASHARELINKAGE = YES\n")
    mcrText.append("  ZONELIST =  [" + str(zoneIndex) + "]\n")
    mcrText.append("  VARPOSITIONLIST =  [1," + str(varIndex) + "]\n")
    mcrText.append("  BINARY = NO\n")
    mcrText.append("  USEPOINTFORMAT = YES\n")
    mcrText.append("  PRECISION = 9\n")
    mcrText.append("  TECPLOTVERSIONTOWRITE = TECPLOTCURRENT\n")
    ## delete current created zone
    mcrText.append("$!DELETEZONES  [" + str(zoneIndex) + "]\n")
    mcrText.append("#######################################\n\n")
    return mcrText


#######################################################
#            Main Function
#######################################################
if __name__ == '__main__':
    ## unit test case
    mcrTexts = []
    ## write mcr file header
    mcrTexts.extend(WriteMcrHeader(""))
    ## load cgns file
    cgnsfile = os.getcwd() + "/sample/solution.cgns"
    mcrTexts.extend(WriteMcrLoadCgnsFile(cgnsfile))
    ## write cp equation
    refPres = 101325.00
    refDens = 1.3899
    refVmag = 60.1
    indPres = 4
    mcrTexts.extend(WritePressureCoeff(refPres, refDens, refVmag, indPres))
    ## output contours
    numZones = 11
    surfZones = [2, 9, 10, 11]
    cpmin = -8.0
    cpmax =  6.0
    numLevels = 14
    delta = float((cpmax-cpmin)/numLevels)
    
    levels = []
    for i in range(numLevels+1):
        levels.append(cpmin+float(i*delta))

    jpgFile1 = os.getcwd() + "/sample/Contour_cp_y+.jpg"
    mcrTexts.extend(WriteMcrOutputContour(numZones, surfZones, 13, levels, "+Y view", jpgFile1))
    jpgFile2 = os.getcwd() + "/sample/Contour_cp_y-.jpg"
    mcrTexts.extend(WriteMcrOutputContour(numZones, surfZones, 13, levels, "-Y view", jpgFile2))

    ## output cp distribution
    sections = [0.2, 0.4, 0.6, 0.8, 1.0, 1.2]
    zoneIndex = 12
    varIndex = 13
    slicePlane = "ZPLANES"
    for section in sections:
        cpDistributionFile = os.getcwd() + "/sample/CpDistribution_" + str(section) + ".dat"
        mcrTexts.extend(WriteMcrVarDistribution(section, zoneIndex, varIndex, slicePlane, cpDistributionFile))

    ## close tec360
    ##mcrTexts.extend(WriteMcrCloseTec360())

    ## output mcr file
    mcrFilename = "./sample/unittest_mcrfile.mcr"
    mcrFile = open(mcrFilename, "w")
    mcrFile.writelines(mcrTexts)
    mcrFile.close()
    
    pass



    

    
