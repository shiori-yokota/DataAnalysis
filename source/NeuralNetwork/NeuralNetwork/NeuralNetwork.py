# -*- coding: utf-8 -*-
#import numpy as np
## ソフトマックス関数
#def softmax(a):
#	# 入力値の中で最大値を取得
#	c = np.max(a)
#	# オーバーフロー対策として、各要素から一番大きな値cを引く
#	exp_a = np.exp(a - c)
#	sum_exp_a = np.sum(exp_a)
#	# 要素の値 / 全体の要素の合計
#	y = exp_a / sum_exp_a

#	return y
#a = [23.0, 0.94, 5.46]
##print (softmax(a))

from sklearn.neural_network import MLPClassifier
import os.path
import xlrd

#* import dataset *#
dtmPath = "..\\..\\..\\db\\Ingredients.xlsx"
testdatasize = 20
OutOfEstimation = [115,127,128,131,208,222,274,279,285,359]

if os.path.exists(dtmPath):
    MatrixDB = xlrd.open_workbook(dtmPath)

for TrialNum in range(20):
	print ("***************************")
	print ("Trial: " + str(TrialNum + 1))
	ExcludeNumber = []
	StatisticsSheet = MatrixDB.sheet_by_index(1)
	# print ("seet name is `" + StatisticsSheet.name + "`")
	row = 2 + testdatasize * TrialNum
	for test_id in range(testdatasize):
		num = StatisticsSheet.cell_value(row + test_id, 1)
		ExcludeNumber.append(num)
		#print (num)

	## separate Train and Test ##
	StatisticsSheet = MatrixDB.sheet_by_index(0)
	# print ("seet name is `" + StatisticsSheet.name + "`")
	SentenceCount = StatisticsSheet.nrows - 1
	MaxColNum = StatisticsSheet.ncols
	Train_X = []
	Train_Y = []
	Test_X = []
	Test_Y = []
	for row in range(SentenceCount):
		if row + 1 not in OutOfEstimation:
			if row + 1 not in ExcludeNumber:
				row = row + 1
				Number = StatisticsSheet.cell_value(row, 0)
				strdtm = []
				for Mcol in range(4, MaxColNum - 1):
					strdtm.append(StatisticsSheet.cell_value(row, Mcol))
				Tool = StatisticsSheet.cell_value(row, MaxColNum - 1)
				Train_X.append(strdtm)
				Train_Y.append(Tool)
			else:
				row = row + 1
				Number = StatisticsSheet.cell_value(row, 0)
				strdtm = []
				for Mcol in range(4, MaxColNum - 1):
					strdtm.append(StatisticsSheet.cell_value(row, Mcol))
				Tool = StatisticsSheet.cell_value(row, MaxColNum - 1)
				Test_X.append(strdtm)
				Test_Y.append(Tool)

	#* NN *#
	clf = MLPClassifier(solver="sgd", random_state=0, max_iter=10000)
	clf.fit(Train_X, Train_Y)

	# Probability estimates.
	pred_proba = clf.predict_proba(Test_X)
	#print (pred_proba[0])
	# Predict using the multi-layer perceptron classifier
	pred = clf.predict(Test_X)
	for i in range(len(pred)):
		print ("No. "+ str(ExcludeNumber[i]) + " : " + pred[i])

	score = clf.score(Test_X, Test_Y)
	print (score)