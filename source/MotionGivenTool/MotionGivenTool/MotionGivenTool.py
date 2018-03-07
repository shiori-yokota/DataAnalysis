# -*- coding: utf-8 -*-
import os.path
import xlrd
from xlutils.copy import copy
import math
import sys
import numpy as np
import matplotlib.pyplot as plt

evmpath = "..\\..\\..\\"
resultpath = "..\\..\\..\\result\\"
SentenceDBFile = evmpath + "db\\MixedDB.xlsx"
ConfigFile = evmpath + "data\\ConfigFile.txt"

class BayesRule:
    def __init__(self):
        self.DBname = ""                # DB's name
        self.MotionDB = ""              # Excel book name
        self.StatisticsSheet = ""       # Excel sheet name
        self.SentenceCount = ""         # number of sentence
        self.ExcludeNumber = []         # exclude number for train phase
        self.OutOfEstimation = []       # out of estimation
        self.TrialNum = ""
        self.testdatasize = 20
        self.MaterialNames = set()
        self.ToolNames = set()
        self.material_tool_count = {}   # {'chopsticks': {'salt': 6, 'suger': 4, ...} }
        self.tool_count = {}            # {'chopsticks': 16, 'hand': 9, ...}
        self.material_motion_count = {} # {'motion_1': {'salt': 6, 'suger': 4, ...} }
        self.motion_count = {}          # {'motion_1': 16, 'motion_2': 9, ...}
        self.motion_tool_count = {}     # {'chopsticks': {'motion_1' : 5, 'motion_2' : 2, ...} }
        self.estimate_tool = {}         # {'ExcludeNumber1' : 'chopsticks', 'ExcludeNumber2' : 'hand', ... }
        

######################################################################
    
    """ check to exit sentence db """ 
    def exitDB(self, name):
        self.DBname = name
        if os.path.exists(self.DBname):
            self.MotionDB = xlrd.open_workbook(self.DBname)
            return True
        else:
            return False        

    """ Road config file """
    def roadConfig(self, name):
        if os.path.exists(name):
            tmp = []
            for line in open(name):
                tmp = line[:-1].split(':')
                #if tmp[0] == 'TestDataNum':
                #    for num in tmp[1].split(','):
                #        self.ExcludeNumber.append(num)
                if tmp[0] == 'TrialNum':
                    self.TrialNum = int(tmp[1])
                elif tmp[0] == 'EstimateTools':
                    if tmp[1] == 'True':
                        self.EstimateTools = True
                elif tmp[0] == 'Log':
                    if tmp[1] == 'False':
                        self.without_log = True
                        print 'without log'
                    else:
                        print 'use log'
                elif tmp[0] == 'LaplaceSmoothing':
                    if tmp[1] == 'False':
                        self.LaplaceSmoothing = False
                        print 'Laplace Smoothing : False'
                    else:
                        print 'Laplace Smoothing : True'
                elif tmp[0] == 'OutOfEstimation':
                    for num in tmp[1].split(','):
                        self.OutOfEstimation.append(num)
                else:
                    continue

    """ Road Test Data """
    def roadTestData(self):
        # print "trial num : %d" % self.TrialNum
        self.StatisticsSheet = self.MotionDB.sheet_by_index(2)
        sentence_row = 2 + self.testdatasize * (self.TrialNum - 1)
        for test_sentence_id in range(self.testdatasize):
            num = self.StatisticsSheet.cell_value(sentence_row + test_sentence_id, 1)
            self.ExcludeNumber.append(num)
            print "id : %d" % num

######################################################################

 
    """ motion and tool count up """
    def motion_tool_count_up(self, ToolName, MotionNumber):
        self.motion_tool_count.setdefault(ToolName, {})
        self.motion_tool_count[ToolName].setdefault(MotionNumber, 0)
        self.motion_tool_count[ToolName][MotionNumber] += 1
 
    """ material and tool count up """
    def material_tool_count_up(self, material, ToolName):
        self.material_tool_count.setdefault(ToolName, {})
        self.material_tool_count[ToolName].setdefault(material, 0)
        self.material_tool_count[ToolName][material] += 1
        self.MaterialNames.add(material)

    """ tool count up """
    def tool_count_up(self, ToolName):
        self.tool_count.setdefault(ToolName, 0)
        self.tool_count[ToolName] += 1

    """ tool and motion count up """
    def material_tool_motion_count_up(self, MotionNumber, ToolName):
        self.material_motion_count[MotionNumber].setdefault(ToolName, 0)
        self.material_motion_count[MotionNumber][ToolName] += 1
        self.ToolNames.add(ToolName)

    """ material motion count up """
    def material_motion_count_up(self, material, MotionNumber):
        self.material_motion_count.setdefault(MotionNumber, {})
        self.material_motion_count[MotionNumber].setdefault(material, 0)
        self.material_motion_count[MotionNumber][material] += 1
        self.MaterialNames.add(material)

    """ motion count up """
    def motion_count_up(self, MotionNumber):
        self.motion_count.setdefault(MotionNumber, 0)
        self.motion_count[MotionNumber] += 1

    """
        train data
        EstimateTools : True  -> between Material and Tool 
        EstimateTools : False -> between Material and Motion
    """
    def TrainData(self, sentence_row):
        sentence_row = sentence_row + 2 # 2 is header count
        Number = self.StatisticsSheet.cell_value(sentence_row, 0)
        ToolName = self.StatisticsSheet.cell_value(sentence_row, 12)
        MotionNumber = self.StatisticsSheet.cell_value(sentence_row, 14)
        Materials = []
        for Mcol in range(4, 12):
            if self.StatisticsSheet.cell_type(sentence_row, Mcol) is 1:
                Materials.append(self.StatisticsSheet.cell_value(sentence_row, Mcol))
        for material in Materials:
            self.material_tool_count_up(material, ToolName)
            self.material_motion_count_up(material, MotionNumber)
        self.material_tool_motion_count_up(MotionNumber, ToolName)
        self.tool_count_up(ToolName)
        self.motion_count_up(MotionNumber)
        self.motion_tool_count_up(ToolName, MotionNumber)
        # print '%d -> tool : %s, motion id : %s' % (int(Number), ToolName, MotionNumber)
        #for i in Materials:
        #    print '%s' % i

    """ 
        train 
        istools : True  -> between Material and Tool 
        istools : False -> between Material and Motion
    """
    def train(self):
        # self.MotionDB = xlrd.open_workbook(self.DBname)
        self.StatisticsSheet = self.MotionDB.sheet_by_index(1)
        self.SentenceCount = self.StatisticsSheet.nrows - 2
        # print 'Sentence Count: %d' % self.SentenceCount

        for train_sentence_row in range(self.SentenceCount):
            if train_sentence_row + 1 not in self.ExcludeNumber:
                if str(train_sentence_row + 1) not in self.OutOfEstimation:
                    self.TrainData(train_sentence_row)
                #else:
                    #print '%s is out of estimation' % str(train_sentence_row + 1)
            else:
                self.estimate_tool.setdefault(train_sentence_row + 1, "")
                # print '%s is estimation' % str(train_sentence_row + 1)


######################################################################
    
    """ num_of_appearance """
    def num_of_appearance(self, motion, tool):
        if motion in self.motion_tool_count[tool]:
            return self.motion_tool_count[tool][motion]
        return 0

    """ plotFig : 
        plot p(j|i = **) = p(motion | tool)
    """
    def plotFig(self):
        x = [1,2,3,4,5,6,7]
        folderName = 'figure\\trial' + str(self.TrialNum) + '\\'
        for tool in self.tool_count.keys():
            plt.figure()
            name = resultpath + folderName + tool + '.png'
            print 'i = %s' % tool
            list = []
            denominator_count = self.tool_count[tool]
            print 'p(%s) = %g' % (tool, denominator_count)
            for motion in sorted(self.motion_count.keys()):
                print 'motion %s givien tool %s' % (motion, tool)
                numerator = self.num_of_appearance(motion, tool)
                # print 'count(%s, %s) = %d' % (motion, tool, numerator)
                prob = float(numerator) / denominator_count
                list.append(prob)
                print 'p(%s|%s) = %g' % (motion, tool, prob)

            plt.plot(x, list)

            plt.ylim(0.0, 1.0)
            plt.savefig(name)
            print name


######################################################################

if __name__ == "__main__":
    br = BayesRule()
    if br.exitDB(SentenceDBFile):
        br.roadConfig(ConfigFile)
        #print '*** plot 400 sentence figure ***'
        #print 'train start'
        #br.train()
        #br.plotFig()
        for trial in range(1):
            br.roadTestData()
            print 'train start'
            br.train()
            br.plotFig()

    else:
        print 'ERROR : %s is not exit.' % SentenceDBFile