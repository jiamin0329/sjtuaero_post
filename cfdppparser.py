#!/usr/local/bin/python
#######################################################
#            File description
#######################################################
#  This class is used to parse infos produced in CFD++.
#  Get toltal/inviscid/viscous drag, lift and moment
#  from following files:
#  1. case.log => get ref values (pressure, temperature,
#                 velocities, etc.)
#                 get boundary infos
#  2. mcfd.info1 => get total/inv/vis forces and moments
#  3. infout1f.inp => get ref geom values and alpha
#  4. infout1f.out => will be used if it is a cl-driver case
#######################################################
#    Date        Author        Comment
#  27-Aug-2017   Jiamin Xu     Initial creation
#  28-Oct-2017   Jiamin Xu     Add Validate()
#  06-Jan-2018   Jiamin Xu     Add symm plane type
#  07-Jan-2018   Jiamin Xu     Add FindWing()
#######################################################
#            Import module
#######################################################
import os
import math
from enum import Enum

#######################################################
#            Constants
#######################################################
const_R = 287.0
const_gamma = 1.4

class SymmetryPlaneType(Enum):
    none    = 0
    xyPlane = 1
    xzPlane = 2

#######################################################
#            Class
#######################################################
class CFDppParser:
    def __init__(self, caseName):
        '''Initialize function'''
        # input files
        self.caseName = caseName
        self.logFileName    = caseName + "/" + caseName + ".log"
        self.info1FileName  = caseName + "/mcfd.info1"
        self.infinFileName  = caseName + "/infout1f.inp"
        self.infoutFileName = caseName + "/infout1f.out"
        ## validate input files
        self.__Validate()
        
        # symmetry plane type
        self.symmPlane = SymmetryPlaneType.none
        self.indexLift = -99
        self.indexDrag = -99 
        self.indexSide = -99
        
        # ref values
        self.refPres = 0.0
        self.refTemp = 0.0
        self.refVels = [0.0, 0.0, 0.0]
        self.refVmag = 0.0
        self.refDens = 0.0
        self.refMach = 0.0

        # bc infos
        self.numBounds = 0
        self.noSlipWalls = []

        # ref geom values
        self.alpha = 0.0
        self.refArea = 0.0
        self.refLength = 0.0
        self.refOrign = [0.0, 0.0, 0.0]
        
        # output results
        self.force_tol = [0.0, 0.0, 0.0]
        self.force_inv = [0.0, 0.0, 0.0]
        self.force_vis = [0.0, 0.0, 0.0]
        self.moment    = [0.0, 0.0, 0.0]

        self.div_moment = 0.0

        # center of pressure
        self.xCenterOfPressure = 0.0

        # boundary id of wing
        self.idUpper = -1
        self.idLower = -1

        pass

    ## Accessor methods
    def GetCaseName(self):
        '''Return case name'''
        return self.caseName

    def GetAlpha(self):
        '''Return angle of attack'''
        return self.alpha

    def GetRefArea(self):
        '''Return reference area'''
        return self.refArea

    def GetNumBounds(self):
        '''Return number of boundaries'''
        return self.numBounds

    def GetNoSlipWalls(self):
        '''Return no-slip walls'''
        return self.noSlipWalls
   
    def GetForceTol(self):
        '''Return total forces
        [0] - x force
        [1] - y force
        [2] - z force'''
        return self.force_tol
    
    def GetForceInv(self):
        '''Return inviscid forces
        [0] - x inviscid force
        [1] - y inviscid force
        [2] - z inviscid force'''
        return self.force_inv

    def GetForceVis(self):
        '''Return viscous forces
        [0] - x viscous force
        [1] - y viscous force
        [2] - z viscous force'''
        return self.force_vis
    
    def GetMoment(self):
        '''Return moments
        [0] - x moment
        [1] - y moment
        [2] - z moment'''
        return self.moment
    
    def GetRefPres(self):
        '''Return reference pressure'''
        return self.refPres
    
    def GetRefTemp(self):
        '''Return reference temperature'''
        return self.refTemp

    def GetRefVels(self):
        '''Return reference velocity
        [0] - x velocity
        [1] - y velocity
        [2] - z velocity'''
        return self.refVels
    
    def GetRefVmag(self):
        '''Return reference velocity magnitude'''
        return self.refVmag
    
    def GetRefDens(self):
        '''Return reference density'''
        return self.refDens
    
    def GetMa(self):
        '''Return freestream mach number'''
        return self.refMach

    def GetCoeffLift(self):
        '''Return lift coefficients
        [0] - total lift coefficient
        [1] - inviscid lift coefficient
        [2] - viscous lift coefficient'''
        Cl = [0.0, 0.0, 0.0]
        coeff_div = 0.5*self.refDens*self.refVmag*self.refVmag*self.refArea
        # lift coeff - total
        Cl[0] = (self.force_tol[self.indexLift]*math.cos(math.radians(self.alpha)) - self.force_tol[self.indexDrag]*math.sin(math.radians(self.alpha)))/coeff_div
        # lift coeff - inviscid
        Cl[1] = (self.force_inv[self.indexLift]*math.cos(math.radians(self.alpha)) - self.force_inv[self.indexDrag]*math.sin(math.radians(self.alpha)))/coeff_div
        # lift coeff - viscous
        Cl[2] = (self.force_vis[self.indexLift]*math.cos(math.radians(self.alpha)) - self.force_vis[self.indexDrag]*math.sin(math.radians(self.alpha)))/coeff_div
        
        return Cl

    def GetCoeffDrag(self):
        '''Return drag coefficients
        [0] - total drag coefficient
        [1] - inviscid drag coefficient
        [2] - viscous drag coefficient'''
        Cd = [0.0, 0.0, 0.0]
        coeff_div = 0.5*self.refDens*self.refVmag*self.refVmag*self.refArea      
        # drag coeff - total
        Cd[0] = (self.force_tol[self.indexLift]*math.sin(math.radians(self.alpha)) + self.force_tol[self.indexDrag]*math.cos(math.radians(self.alpha)))/coeff_div
        # drag coeff - invicid
        Cd[1] = (self.force_inv[self.indexLift]*math.sin(math.radians(self.alpha)) + self.force_inv[self.indexDrag]*math.cos(math.radians(self.alpha)))/coeff_div
        # drag coeff - viscous
        Cd[2] = (self.force_vis[self.indexLift]*math.sin(math.radians(self.alpha)) + self.force_vis[self.indexDrag]*math.cos(math.radians(self.alpha)))/coeff_div
        
        return Cd

    def GetLDRatio(self):
        '''Return Lift/Drag ratio'''
        cl = self.GetCoeffLift()
        cd = self.GetCoeffDrag()
        ld = cl[0]/cd[0]
        return ld

    def GetCoeffMoment(self):
        '''Return moment coefficient'''
        coeff_div = 0.5*self.refDens*self.refVmag*self.refVmag*self.refArea*self.refLength
        Cm = ((self.moment[self.indexSide] + self.force_tol[self.indexLift]*self.refOrign[self.indexDrag] - self.force_tol[self.indexDrag]*self.refOrign[self.indexLift]))/coeff_div
        return Cm
    
    def GetCenterOfPressure(self):
        return self.moment[self.indexSide]/self.force_tol[self.indexLift]

    def GetWingBoundaryIds(self):
        wings = []
        wings.append(self.idUpper)
        wings.append(self.idLower)
        return wings

    ## main methods    
    def __Validate(self):
        '''Validate all dependency files'''
        isValidated = True

        ## validate folder
        if not os.path.exists(self.caseName):
            isValidated = False

        ## validate files
        ## check log file
        if isValidated:
            if not os.path.exists(self.logFileName):
                print("File not Found:" + self.logFileName)
                isValidated = False

        ## check mcfd.info1 file
        if isValidated:
            if not os.path.exists(self.info1FileName):
                print("File not Found:" + self.info1FileName)
                isValidated = False

        ## check infout1f file
        if isValidated:
            if not os.path.exists(self.infinFileName) and \
               not os.path.exists(self.infoutFileName):
                print("File not Found:" + self.infinFileName + " or " + self.infoutFileName)
                isValidated = False

        return isValidated

    def IsClDriverCase(self):
        '''Check if it is a CL-driver case'''
        isClDriverCase = False
        try:
            inpFile = open(self.logFileName)
            inpTexts = inpFile.readlines()

            for i in range(len(inpTexts)):
                if "cldriver_controls" in inpTexts[i]:
                    isClDriverCase = True
                    break
            inpFile.close()
            
        except Exception as e:
            print(e)
            exit(1)

        return isClDriverCase

    def Process(self):
        # processing datas
        self.__ReadRefVals()
        self.__ReadBcInfos()
        self.__ReadRefGeomVals()
        self.__ReadForces()
        pass

    def __ReadRefVals(self):
        '''Read reference valuse from log file'''
        try:
            logFile = open(self.logFileName)
            lines = logFile.readlines()
        
            for line in lines:
                # get ref pressure
                if "aero_pres" in line and len(line.split()) == 3:
                    self.refPres = float(line.split()[2])
                    
                # get ref temperature
                if "aero_temp" in line and len(line.split()) == 3:
                    self.refTemp = float(line.split()[2])

                # get ref velocities
                if "aero_u" in line and len(line.split()) == 3:
                    self.refVels[0] = float(line.split()[2])
                if "aero_v" in line and len(line.split()) == 3:
                    self.refVels[1] = float(line.split()[2])
                if "aero_w" in line and len(line.split()) == 3:
                    self.refVels[2] = float(line.split()[2])

            # get velocity magnitude
            for vel in self.refVels:
                self.refVmag += vel*vel
            self.refVmag = math.sqrt(self.refVmag)

            # get ref density
            self.refDens = self.refPres/const_R/self.refTemp

            # get ref mach number
            sound_speed = math.sqrt(const_gamma*const_R*self.refTemp)
            self.refMach =  self.refVmag/sound_speed
               
            logFile.close()
            
        except Exception as e:
            print(e)
            exit(1)

    def __ReadBcInfos(self):
        '''Get bc infos from log file'''
        try:
            logFile = open(self.logFileName)
            lines = logFile.readlines()

            # get total number of boundaries
            for line in lines:
                if "mbcons" in line and len(line.split()) == 3:
                    self.numBounds = int(line.split()[2])
                    break

            # get no-slip walls
            staIndex = 0
            for line in lines:
                if "# No-slip adiabatic wall" in line:
                    staIndex = lines.index(line, staIndex, len(lines))
                    noSlipWall = lines[staIndex-2].split()[1]
                    self.noSlipWalls.append(int(noSlipWall))
                    staIndex = staIndex + 1
                    
            logFile.close()
            
        except Exception as e:
            print(e)
            exit(1)

    def __ReadRefGeomVals(self):
        '''Return aerodynamic reference values'''
        try:
            infFileName = ""
            if self.IsClDriverCase():
                infFileName = self.infoutFileName
            else:
                infFileName = self.infinFileName

            infFile = open(infFileName)
            lines = infFile.readlines()

            for line in lines:
                if "alpha" in line:
                    self.alpha = float(line.split()[1])
                if "axref" in line:
                    self.refArea = float(line.split()[1])
                if "lxref" in line:
                    self.refLength = float(line.split()[1])
                if "xcen" in line:
                    self.refOrign[0] = float(line.split()[1])
                if "ycen" in line:
                    self.refOrign[1] = float(line.split()[1])
                if "zcen" in line:
                    self.refOrign[2] = float(line.split()[1])
                if "plane" in line:
                    plane = line.split()[1]
                    if plane == "xy":
                        self.SymmPlaneType = SymmetryPlaneType.xyPlane
                        self.indexDrag = 0
                        self.indexLift = 1
                        self.indexSide = 2
                    else:
                        self.SymmPlaneType = SymmetryPlaneType.xzPlane
                        self.indexDrag = 0
                        self.indexLift = 2
                        self.indexSide = 1
                        
            infFile.close()
            
        except Exception as e:
            print(e)
            exit(1)
            
    def __ReadForces(self):
        '''Read forces from mcfd.info1 file'''
        try:
            info1File = open(self.info1FileName)
            lines = info1File.readlines()
            numLines = len(lines)
            staIndex = numLines-23*self.numBounds+1

            for ibc in range(self.numBounds):
                blockIndex = staIndex+ibc*23
                if ibc+1 in self.noSlipWalls:
                    # force x
                    self.force_tol[0]  += float(lines[blockIndex+3].split()[2])
                    self.force_inv[0]  += float(lines[blockIndex+3].split()[3])
                    self.force_vis[0]  += float(lines[blockIndex+3].split()[4])

                    # force y
                    self.force_tol[1]  += float(lines[blockIndex+4].split()[2])
                    self.force_inv[1]  += float(lines[blockIndex+4].split()[3])
                    self.force_vis[1]  += float(lines[blockIndex+4].split()[4])

                    # force z
                    self.force_tol[2]  += float(lines[blockIndex+5].split()[2])
                    self.force_inv[2]  += float(lines[blockIndex+5].split()[3])
                    self.force_vis[2]  += float(lines[blockIndex+5].split()[4])

                    # x/y/z moment
                    self.moment[0] += float(lines[blockIndex+6].split()[2])
                    self.moment[1] += float(lines[blockIndex+7].split()[2])
                    self.moment[2] += float(lines[blockIndex+8].split()[2])
    
            info1File.close()
            
        except Exception as e:
            print(e)
            exit(1)
            
        
    def FindWing(self):
        '''Find boundary id of wing'''
        isWingUpperFound = False
        isWingLowerFoudn = False
        
        inpFile = open(self.logFileName)
        inpTexts = inpFile.readlines()

        for i in range(len(inpTexts)):
            if "WINGUPPER" in inpTexts[i]:
                self.idUpper = int(inpTexts[i].split()[0])
                isWingUpperFound = True
            if "WINGLOWER" in inpTexts[i]:
                self.idLower = int(inpTexts[i].split()[0])
                isWingLowerFound = True

        return isWingUpperFound and isWingLowerFound
        
#######################################################
#            Main Function
#######################################################
if __name__ == '__main__':
    '''unit test case'''
    cfdppParser = CFDppParser("sample")
    cfdppParser.Process()
    
    print( "                 Case Name: "+ cfdppParser.GetCaseName()             )
    print( "            Cl-driver case: "+ str(cfdppParser.IsClDriverCase())     )
    print( "    Total number of bounds: "+ str(cfdppParser.GetNumBounds())       )
    print( "             No-slip walls: "+ str(cfdppParser.GetNoSlipWalls())     )
    print( "           Angle of attack: "+ str(cfdppParser.GetAlpha())           )
                                                                                
    print( "          Lift Coefficient: "+ str(cfdppParser.GetCoeffLift())       )
    print( "          Drag Coefficient: "+ str(cfdppParser.GetCoeffDrag())       )
    print( "        Moment Coefficient: "+ str(cfdppParser.GetCoeffMoment())     )
    print( "                       L/D: "+ str(cfdppParser.GetLDRatio())         )
                                                                                
    print( "                     Force: "+ str(cfdppParser.GetForceTol())        )
    print( "                    Moment: "+ str(cfdppParser.GetMoment())          )
    print( "Center of Pressure (x-dir): "+ str(cfdppParser.GetCenterOfPressure()))
        
