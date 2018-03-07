# -*- coding: utf-8 -*- #
import glob
from hmmlearn import hmm
import numpy as np
from sklearn.mixture import GMM
from sklearn.externals import joblib, joblib
import sklearn


EvmPath = "..\\..\\..\\"

compornents = 8 ## State number of HMM
mix = 10 ## Mixture number of GMM

LearningData = []
#### LEARNING ####
for motionID in glob.glob(EvmPath + 'MotionData\\Learning\\*'):
	print("Motion id: " + str(motionID))
	models = []

	'''
	GMMHMM(algorithm='viterbi', covariance_type='diag', covars_prior=0.01,
		init_params='stmcw', n_components=5, n_iter=10, n_mix=1,
		params='stmcw', random_state=None, startprob_prior=1.0, tol=0.01,
		transmat_prior=1.0, verbose=False)
		init_params : string, optional
			Controls which parameters are initialized prior to training. Can
			contain any combination of 's' for startprob, 't' for transmat, 'm'
			for means, 'c' for covars, and 'w' for GMM mixing weights.
			Defaults to all parameters.
		params : string, optional
			Controls which parameters are updated in the training process.  Can
			contain any combination of 's' for startprob, 't' for transmat, 'm' for
			means, and 'c' for covars, and 'w' for GMM mixing weights.
			Defaults to all parameters.
	'''
	model = hmm.GMMHMM(n_components = compornents, n_iter = 100, n_mix = mix,
					verbose = True, init_params = 'cmw', params = 'mctw', covariance_type = 'full')

	transmat = np.zeros((compornents, compornents))

	## Left-to-right: each state is connected to itself and its direct successor.
	## Correct left-to-right model
	for i in range(compornents):
		if i == compornents - 1:
			transmat[i, i] = 1.0
		else:
			transmat[i, i] = transmat[i, i + 1] = 0.5

	print(transmat)
	## Always start in first state
	startprob = np.zeros(compornents)
	startprob[0] = 1.0

	model.transmat_ = transmat
	model.startprob_ = startprob

	gmms = []
	for i in range(0, compornents):
		gmms.append(sklearn.mixture.GMM())
	model.gmms_ = gmms

	## motion data ##
	motions = []
	lengths = []
	for file in glob.glob(motionID+'\\*.dat'):
		print(file)
		motion = []
		escapes = []
		for line in open(file):	## select motion
			if '0.0,11,0' in line:
				print('header: ' + str(line))
				headerName = line[:-1].split('\t')
				for i, item in enumerate(headerName):
					if 'Avatar' in item:
						escapes.append(i)
			else:
				data = line[:-1].split('\t')
				# print('data: '+str(data))
				tmpPose = []
				for i, item in enumerate(data):
					if i in escapes:
						# print(i, item)
						tmpItem = item[:-1].split(',')
						for j in tmpItem:
							tmpPose.append(float(j))
				motion.append(tmpPose)
		motions.append(motion)
		lengths.append(len(motion))

	## CREATE HMM PARAMETER ##
	X = np.concatenate(motions)
	model.fit(X, lengths)
	print(model.transmat_)
	for line in model.transmat_:
		sum = 0.0
		for one in line:
			sum += one
		print('sum: ' + str(format(sum, '.15f')))
		if round(sum, 4) != 1.0:
			input('check sum error >>> ')
	models.append(model)
	joblib.dump(model, motionID + '\\' + motionID[-1:] + '.pkl')

