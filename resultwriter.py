#!/usr/local/bin/python
#######################################################
#            File description
#######################################################
#  This class is used to output all results into a
#  xls file.
#######################################################
#    Date        Author        Comment
#  27-Aug-2017   Jiamin Xu     Initial creation
#  19-Nov-2017   Jiamin Xu     Add center of pressure
#  19-Nov-2017   Jiamin Xu     Add wing root blending moment
#######################################################
#            Import module
#######################################################
from xlutils.copy import copy
import xlwt
import xlrd

#######################################################
#            Constants
#######################################################

#######################################################
#            Class
#######################################################
class ResultWriter:
    def __init__(self, filename):
        '''Initialize function'''
        try:
            self.resultFilename = filename
            self.book = xlwt.Workbook(encoding="utf-8")
            self.sheet1 = self.book.add_sheet("Aerodynamic Data")
            self.__WriteSheet1()
            self.book.save(self.resultFilename)
        except Exception as e:
            print (e)
            exit(1)

            
    def __WriteSheet1(self):
        '''Write sheet1 headers'''
        try:
            ## write sheet header
            self.sheet1.write(0,  0, "Case")
            self.sheet1.write(0,  1, "Ma")
            self.sheet1.write(0,  2, "Alpha")
            self.sheet1.write(0,  3, "Cl")
            self.sheet1.write(0,  4, "Cd")
            self.sheet1.write(0,  5, "L/D")
            self.sheet1.write(0,  6, "Cd_inv")
            self.sheet1.write(0,  7, "Cd_vis")
            self.sheet1.write(0,  8, "Cm")
            self.sheet1.write(0,  9, "Cd_ind")
            self.sheet1.write(0, 10, "Cd_wav")
            self.sheet1.write(0, 11, "Cd_pro")
            self.sheet1.write(0, 12, "WingRootBlendingMoment")
            self.sheet1.write(0, 13, "Center of Pressure")
        except Exception as e:
            print (e)
            exit(1)

            
    def AddCase(self, caseName, ma, alpha, cl, cd, ldratio, cd_inv, cd_vis, cm, cd_ind, cd_wav, cd_pro, wrbm, centerOfPressure):
        '''Add data into sheet1'''
        try:
            originalBook = xlrd.open_workbook(self.resultFilename)
            copiedBook = copy(originalBook)
            sheet = copiedBook.get_sheet(0)
            row =len(sheet.get_rows())

            sheet.write(row,  0, caseName)
            sheet.write(row,  1, ma)
            sheet.write(row,  2, alpha)
            sheet.write(row,  3, cl)
            sheet.write(row,  4, cd)
            sheet.write(row,  5, ldratio)
            sheet.write(row,  6, cd_inv)
            sheet.write(row,  7, cd_vis)
            sheet.write(row,  8, cm)
            sheet.write(row,  9, cd_ind)
            sheet.write(row, 10, cd_wav)
            sheet.write(row, 11, cd_pro)
            sheet.write(row, 12, wrbm)
            sheet.write(row, 13, centerOfPressure)

            copiedBook.save(self.resultFilename)
            
        except Exception as e:
            print (e)
            exit(1)
            
#######################################################
#            Main Function
#######################################################
if __name__ == '__main__':
    resultWriter = ResultWriter("test.xls")
    resultWriter.AddCase("test1", 0.85, 2.2, 0.48, 0.0208, 2, 1, 2.0, 111.0, "N/A", "N/A", "N/A", 0.0, 0.0)
    
