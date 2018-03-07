# -*- coding: utf-8 -*-
import xlwt
import glob
import numpy as np
from sklearn.externals import joblib, joblib
import sklearn

EvmPath = '..\\..\\..\\'
book = xlwt.Workbook()
sheet = book.add_sheet('Sheet_1')
#book.save('sample.xls')

MotionData = []
## Load test data ##
for file in glob.glob(EvmPath + 'MotionData\\Collecting\\*.dat'):
	MotionData.append(file)
print('Test data num: ' + str(len(MotionData)))

## Load HMM model ##
HMMmodels = []
for motionID in glob.glob(EvmPath + 'MotionData\\Learning\\*'):
	for file in glob.glob(motionID + '\\*.pkl'):
		HMMmodels.append(file)
print('HMM model num: ' + str(len(HMMmodels)))

for i in MotionData:
	TestData = MotionData.pop(0)
	print('DATA: ' + TestData)

	## select test motion data ##
	tmpName = TestData.split('\\')
	fileName = ''
	for item in tmpName:
		if '.dat' in item:
			fileName = item
	print('Test data: ' + fileName)
	motion = []
	escapes = []
	for line in open(TestData):	## select motion
		if '0.0,11,0' in line:
			# print('heade: ' + str(line))
			headerName = line[:-1].split('\t')
			for i, item in enumerate(headerName):
				if 'Avatar' in item:
					escapes.append(i)
		else:
			data = line[:-1].split('\t')
			# print('data: ' + str(data))
			tmpPose = []
			for i, item in enumerate(data):
				if i in escapes:
					# print(i, item)
					tmpItem = item[:-1].split(',')
					for j in tmpItem:
						tmpPose.append(float(j))
			motion.append(tmpPose)

	scores = []
	for modelCount, model in enumerate(HMMmodels):
		print(modelCount, model)
		HMM = joblib.load(model)
		tmpName = model.split('\\')
		motionName = tmpName[-2]
		try:
			print('motion id ' + motionName + ' likehood: ' + str(HMM.score(motion)))
			tmp = [(float(str(HMM.score(motion)))), motionName]
			scores.append(tuple(tmp))
		except Exception as e:
			print(e)

	## ranking 1st is motion label
	max = -1.0e+15
	index = 0
	ranking = sorted(scores)
	ranking.reverse()
	print('----------RANK----------')
	for rank in ranking:
		print(rank)
	print('Label of this motion is ... ' + str(ranking[0][1]))