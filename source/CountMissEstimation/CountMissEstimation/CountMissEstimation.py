# -*- coding: utf-8 -*-
import os.path
import xlrd
import math
import sys

evmpath = "..\\..\\..\\"
SentenceDBFile = evmpath + "db\\MixedDB.xlsx"

class BayesRule:
    def __init__(self):
        self.DBname = ""                # DB's name
        self.MotionDB = ""              # Excel book name
        self.StatisticsSheet = ""       # Excel sheet name
        self.SentenceCount = ""
        self.CountNotEstimateMotionID = 0
        self.CountNotEstimateToolName = 0
        self.CountNotEstimateMotionIDwithTool = 0

######################################################################
    
    """ check to exit sentence db """ 
    def exitDB(self, name):
        self.DBname = name
        if os.path.exists(self.DBname):
            self.MotionDB = xlrd.open_workbook(self.DBname)
            return True
        else:
            return False

    """ check result """
    def checkResult(self, sentence_row):
        sentence_row = sentence_row + 2
        Number = self.StatisticsSheet.cell_value(sentence_row, 1)
        CorrectToolName = self.StatisticsSheet.cell_value(sentence_row, 2)
        CorrectMotionID = self.StatisticsSheet.cell_value(sentence_row, 3)
        EstimateMotionID = self.StatisticsSheet.cell_value(sentence_row, 4)
        EstimateToolName = self.StatisticsSheet.cell_value(sentence_row, 5)
        EstimateMotionIDwithTool = self.StatisticsSheet.cell_value(sentence_row, 6)

        if str(CorrectMotionID) != str(EstimateMotionID):
            print Number

    """ road data """
    def roadData(self):
        self.StatisticsSheet = self.MotionDB.sheet_by_index(3)
        print self.MotionDB.sheet_by_index(3).name
        self.SentenceCount = self.StatisticsSheet.nrows - 2
        for sentence_id in range(self.SentenceCount):
            self.checkResult(sentence_id)


if __name__ == "__main__":
    br = BayesRule()
    if br.exitDB(SentenceDBFile):
        br.roadData()
    else:
        print 'ERROR : %s is not exit.' % SentenceDBFile