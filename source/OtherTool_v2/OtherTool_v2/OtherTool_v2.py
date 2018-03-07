# -*- coding: utf-8 -*-
import os.path
import xlrd
from xlutils.copy import copy
import math
import sys

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
        self.cpMotionDB = ""            # to edit existing excel documents
        self.EstimateTools = True
        self.wasEstimateTools = False
        self.without_log = False
        self.LaplaceSmoothing = False
        self.UsingOtherTool = True
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
        self.estimate_tool = {}         # {'ExcludeNumber1' : 'chopsticks', 'ExcludeNumber2' : 'hand', ... }
        self.denominator = 0.0

    def reset(self):
        self.roadConfig(ConfigFile)
        self.ExcludeNumber = []         # exclude number for train phase
        self.OutOfEstimation = []
        self.MaterialNames = set()
        self.ToolNames = set()
        self.material_tool_count = {}   # {'chopsticks': {'salt': 6, 'suger': 4, ...} }
        self.tool_count = {}            # {'chopsticks': 16, 'hand': 9, ...}
        self.material_motion_count = {} # {'motion_1': {'salt': 6, 'suger': 4, ...} }
        self.motion_count = {}          # {'motion_1': 16, 'motion_2': 9, ...}
        self.estimate_tool = {}         # {'ExcludeNumber1' : 'chopsticks', 'ExcludeNumber2' : 'hand', ... }
        self.denominator = 0.0


######################################################################
    
    """ check to exit sentence db """ 
    def exitDB(self, name):
        self.DBname = name
        if os.path.exists(self.DBname):
            self.MotionDB = xlrd.open_workbook(self.DBname)
            self.cpMotionDB = copy(self.MotionDB)
            return True
        else:
            return False        

    """ Road config file """
    def roadConfig(self, name):
        if os.path.exists(name):
            tmp = []
            for line in open(name):
                tmp = line[:-1].split(':')
                if tmp[0] == 'TrialNum':
                    self.TrialNum = int(tmp[1])
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
            #print "id : %d" % num

######################################################################

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
        #print '%d -> tool : %s, motion id : %s' % (int(Number), ToolName, MotionNumber)
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
                #   print '%s is out of estimation' % str(train_sentence_row + 1)
            else:
                self.estimate_tool.setdefault(train_sentence_row + 1, "")


######################################################################

    """ MarginalProbability : 
        if self.EstimateTools is True  : p(material)
            p(X) = sigma_i(p(i)p(material|i)p(material|i))
        if self.EstimateTools is False :
            if self.wasEstimationTools is True  : p(material, tool)
                p(X, t) = sigma_j(p(j)p(material|j)p(material|j)p(t|j)
            if self.wasEstimationTools is False : p(material)
                p(X) = sigma_j(p(j)p(material|j)p(material|j))
    """
    def MarginalProbability(self, materials, number):
        print 'marginal probability : %s' % number
        prob = 0.0;
        if self.EstimateTools:
            for tool in self.tool_count.keys():
                score = self.prior_prob(tool)
                # print 'p(%s) = %g' % (tool, score)
                for material in materials:
                    # print 'p(%s | %s) = %g' % (material, tool, self.likelihood_prob(material, tool))
                    score *= self.likelihood_prob(material, tool)
                # print 'score = %g' % score
                prob += score
            # print 'sum = %g\n' % prob
        else:
            for motion in sorted(self.motion_count.keys()):
                score = self.prior_prob(motion)
                # print 'p(%s) = %g' % (motion, score)
                for material in materials:
                    # print 'p(%s | %s) = %g' % (material, motion, self.likelihood_prob(material, motion))
                    score *= self.likelihood_prob(material, motion)
                if self.wasEstimateTools:
                    # print 'p(%s | %s) = %g' % (self.estimate_tool[number], motion, self.likelihood_prob(self.estimate_tool[number], motion))
                    score *= self.likelihood_prob(self.estimate_tool[number], motion)
                # print 'score = %g' % score
                prob += score
            # print 'sum = %g\n' % prob
        return prob

    def multiplication(self, prob_list):
        score = prob_list[0]
        for num in range(1, len(prob_list)):
            score *= prob_list[num]
        return score

    """ denominator : p(X)
        if self.EstimateTools is True  : p(material)p(material)
        if self.EstimateTools is False : p(material)p(material)p(tool)
    """
    def denominator_prob(self, category):
        count = 0
        for key in self.material_motion_count.iterkeys():
            # print 'key : %s, category : %s' % (key, category)
            if category in self.material_motion_count[key]:
                count += self.material_motion_count[key][category]
        # print '%s appear %d time' % (category, count)
        score = float(count) / sum(self.motion_count.values())
        # print 'p(%s) = %g' % (category, score)
        return score

    """ number of appearance """
    def num_of_appearance(self, material, category):
        if self.EstimateTools:
            if material in self.material_tool_count[category]:
                return self.material_tool_count[category][material]
            return 0
        else:
            if material in self.material_motion_count[category]:
                return self.material_motion_count[category][material]
            return 0

    """ likelihood_prob : bayes rule -> p(X | Y) = p(material | category) 
        if self.EstimateTools is True  : p(material | tool)
        if self.EstimateTools is False :
            if self.wasEstimationTools is True  : p(material, tool | motion)
            if self.wasEstimationTools is False : p(material | motion)    
    """
    def likelihood_prob(self, material, category):
        laplaceSmoothing = 0
        if self.LaplaceSmoothing:
            laplaceSmoothing = 1
        if self.EstimateTools:
            numerator = self.num_of_appearance(material, category) + laplaceSmoothing # + 1 is Laplace Smoothing
            # print 'count(%s , %s) = %d' % (material, category, numerator)
            # denominator = sum(self.material_tool_count[category].values()) + len(self.MaterialNames) # naive bayes
            denominator = self.tool_count[category]
            prob = float(numerator) / denominator
            # print 'p(%s | %s) : %s\n' % (material, category, str(prob))
            # f.write('%s, %s : %s\n' % (material.encode('utf-8'), category.encode('utf-8'), str(prob)))
            return prob
        else:
            numerator = self.num_of_appearance(material, category) + laplaceSmoothing # + 1 is Laplace Smoothing
            # print 'count(%s , %s) = %d' % (material, category, numerator)
            # denominator = sum(self.material_motion_count[category].values()) + len(self.MaterialNames) # naive bayes
            denominator = self.motion_count[category]
            # print 'denominator = %s' % denominator
            prob = float(numerator) / denominator
            # print 'p(%s | %s) : %s' % (material, category, str(prob))
            # f.write('%s, %s : %s\n' % (material.encode('utf-8'), category.encode('utf-8'), str(prob)))
            return prob

    """ prior_prob : p(Y) = p(category)
        if self.EstimateTools is True  : p(toolName)
        if self.EstimateTools is False : p(motionID)
    """
    def prior_prob(self, category):
        if self.EstimateTools:
            num_of_tools = sum(self.tool_count.values())
            num_of_material_of_the_tool = self.tool_count[category]
            # print "%s : %d / %d -> %g" % (category, num_of_material_of_the_tool, num_of_tools, float(num_of_material_of_the_tool) / num_of_tools)
            return float(num_of_material_of_the_tool) / num_of_tools
        else:
            num_of_motions = sum(self.motion_count.values())
            num_of_material_of_the_motion = self.motion_count[category]
            # print "motion_%s : %d / %d -> %g" % (category, num_of_material_of_the_motion, num_of_motions, float(num_of_material_of_the_motion) / num_of_motions)
            return float(num_of_material_of_the_motion) / num_of_motions

    """ score """
    def score(self, number, materials, category):
        score = math.log(self.prior_prob(category))
        denominator_list = []
        # print 'log score is : %g' % score
        for material in materials:
            score += math.log(self.likelihood_prob(material, category))
            denominator_list.append(self.denominator_prob(material))
        if self.wasEstimateTools:
            # print self.estimate_tool[number]
            score += math.log(self.likelihood_prob(self.estimate_tool[number], category))
            denominator_list.append(self.denominator_prob(self.estimate_tool[number]))
        # score / denominator -> log(score) - log(denominator)
        prob = score - math.log(self.multiplication(denominator_list))
        print 'p(%s | X) = %g' % (category, prob)
        return prob

    """ score without log """
    def score_without_log(self, number, materials, category):
        score = self.prior_prob(category)
        denominator_list = []
        for material in materials:
            score *= self.likelihood_prob(material, category)
            denominator_list.append(self.denominator_prob(material))
        if self.wasEstimateTools:
            # print self.estimate_tool[number]
            score *= self.likelihood_prob(self.estimate_tool[number], category)
            denominator_list.append(self.denominator_prob(self.estimate_tool[number]))
        # print 'score = %g' % score
#        prob = score / self.multiplication(denominator_list)
        prob = score / self.denominator;
        print 'p(%s | X) = %g' % (category, prob)
        return prob

    """ classify """
    def classify(self):
        test_sentence_num = self.ExcludeNumber
        fileName = ""
        if self.EstimateTools:
            fileName = resultpath + 'trial' + str(self.TrialNum) + '\\' + 'Result_ExcludeSecondTool_v2.txt'
        else:
            if self.wasEstimateTools:
                fileName = resultpath + 'trial' + str(self.TrialNum) + '\\' + 'Result_ExcludeMotion_with_Secondtool_v2.txt'
            else:
                fileName = resultpath + 'trial' + str(self.TrialNum) + '\\' + 'Result_ExcludeMotion_v2.txt'
        print fileName
        f = open(fileName, 'w')
        WriteStatisticsSheet = self.cpMotionDB.get_sheet(3)
        write_row = 2 + self.testdatasize * (self.TrialNum - 1)

        for num in range(len(test_sentence_num)):
            best_guessed_target = None
            second_target = None
            max_prob_before = -sys.maxsize
            second_prob = -sys.maxsize

            sentence_row = int(test_sentence_num[num]) + 1
            Number = self.StatisticsSheet.cell_value(sentence_row, 0)
            Materials = []
            f.write('classify sentence number is %s\n' % test_sentence_num[num])
            print 'classify sentence number is %s' % test_sentence_num[num]
            for Mcol in range(4, 12):
                if self.StatisticsSheet.cell_type(sentence_row, Mcol) is 1:
                    # print self.StatisticsSheet.cell_value(sentence_row, Mcol)
                    Materials.append(self.StatisticsSheet.cell_value(sentence_row, Mcol))
            if self.EstimateTools:
                self.denominator = self.MarginalProbability(Materials, test_sentence_num[num])
                for tool in self.tool_count.keys():
                    if self.without_log:
                        prob = self.score_without_log(test_sentence_num[num], Materials, tool)
                    else:
                        prob = self.score(test_sentence_num[num], Materials, tool)
                    f.write('%s : %s\n' % (tool.encode('utf-8'), str(prob)))
                    if prob > max_prob_before:
                        second_prob = max_prob_before
                        second_target = best_guessed_target
                        max_prob_before = prob
                        best_guessed_target = tool
                    elif prob > second_prob:
                        second_prob = prob
                        second_target = tool


                f.write('best tool is %s\n' % best_guessed_target.encode('utf-8'))
                f.write('second tool is %s\n\n' % second_target.encode('utf-8'))
                print 'best tool is %s' % best_guessed_target
                print 'second tool is %s\n' % second_target
                # write db #
                WriteStatisticsSheet.write(write_row + num, 7, second_target)

                self.estimate_tool[test_sentence_num[num]] = second_target
            else:
                print 'Using %s' % self.estimate_tool[test_sentence_num[num]]
                f.write('using : %s\n' % self.estimate_tool[test_sentence_num[num]].encode('utf-8'))
                self.denominator = self.MarginalProbability(Materials, test_sentence_num[num])
                for motion in sorted(self.motion_count.keys()):
                    if self.without_log:
                        prob = self.score_without_log(test_sentence_num[num], Materials, motion)
                    else:
                        prob = self.score(test_sentence_num[num], Materials, motion)
                    f.write('%s : %s\n' % (motion.encode('utf-8'), str(prob)))
                    if prob > max_prob_before:
                        max_prob_before = prob
                        best_guessed_target = motion

                f.write('best motion id is %s\n\n' % best_guessed_target.encode('utf-8'))
                print 'best motion id is %s\n' % best_guessed_target
                # write db #
                if self.wasEstimateTools:
                    WriteStatisticsSheet.write(write_row + num, 8, best_guessed_target)
                else:
                    WriteStatisticsSheet.write(write_row + num, 9, best_guessed_target)


        f.close()
        name = evmpath + "result\\motiondb_v2.xls"
        self.cpMotionDB.save(name)
 

######################################################################

if __name__ == "__main__":
    br = BayesRule()
    if br.exitDB(SentenceDBFile):
        br.roadConfig(ConfigFile)
        br.roadTestData()
        if br.EstimateTools:
            print "material -> tool"
            br.train()
            print "finish train phase"
            br.classify()
            print "material and tool -> motion"
            br.wasEstimateTools = True
            br.EstimateTools = False
            br.classify()

    else:
        print 'ERROR : %s is not exit.' % SentenceDBFile