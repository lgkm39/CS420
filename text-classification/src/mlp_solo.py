# coding=utf-8

import numpy as np
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.neural_network import MLPClassifier
from sklearn.linear_model import SGDClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import roc_auc_score
from sklearn.metrics import roc_curve
from sklearn.model_selection import GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn import datasets
from xgboost import XGBClassifier
import matplotlib.pyplot as plt

def scanner (file_ptr) :
	corpus = []
	labels = []
	
	while True :
		sstr = file_ptr.readline()
		if len(sstr) == 0 :
			break
		else :
			labels.append(int(sstr.split()[0]))
			corpus.append(sstr.split()[1])

	return [corpus, labels]


def compress (X, Y) :
	res = []
	p = 0.27;
	for i in range(len(X)) :
		res.append(X[i] * (1 - p) + float(Y[i]) * p)

	return res


def extract (pred) :
	pred_1 = []

	for p in pred :
		pred_1.append(float(p[1]))

	return pred_1

def visualize_presum (X, Y, fn) :
#	cost_visual = open("./data/cost_visual.txt", "w")	
	V = []
	D = []
	for i in range(len(X)) :
		V.append(abs(X[i] - Y[i]))
	V.sort()
	
	for i in range(len(X)) :
		D.append(V[i])
		if i > 0 :
			D[i] += D[i - 1] 
#	print >> cost_visual, cost_contr
	plt.plot(V, D)
	plt.savefig("./out/" + fn)
	
def compress_all( V, VL ) :
	tot = 0
	res = []
	for i in range(len(V)) :
		tot += V[i]
		for j in range(len(VL[i])) :
			val = float(VL[i][j]) * (float(V[i]))
			if i == 0 :
				res.append(val)
			else :
				res[j] += val

	for i in range(len(res)) :
		res[i] /= tot
	return res
	
	
def main() :
	train_data = open("./data/train.txt", "r")
	eval_data = open("./data/eval.txt", "r")

	raw = scanner(train_data)
	vectorizer = CountVectorizer(analyzer = 'char')
	transformer = TfidfTransformer()
	vectorizer.fit(raw[0])
	transformer.fit(vectorizer.transform(raw[0]))

	train_features = transformer.transform(vectorizer.transform(raw[0]))
	train_labels = raw[1]

	raw = scanner(eval_data)
	eval_features = transformer.transform(vectorizer.transform(raw[0]))
	eval_labels = raw[1]

	mlp = MLPClassifier(solver = 'lbfgs')
	
	parameters = {
		'activation' : ('logistic', 'tanh', 'relu'), 
		'tol' : (1e-4, 1e-5, 1e-6),
		'alpha' : (1e-4, 1e-5, 1e-6),
	}

	grid_search = GridSearchCV(mlp, parameters, cv = 3)
	grid_search.fit(train_features, train_labels)
	
	print "best score: ", grid_search.best_score_
	
	best_mlp = grid_search.best_estimator_				
	best_mlp.fit(train_features, train_labels) 
	pred_m = extract(best_mlp.predict_proba(eval_features))

	print "Multi-Layer Perception: ", roc_auc_score(eval_labels, pred_m)

	best_parameters = dict()
	best_parameters = grid_search.best_estimator_.get_params()
	print ">>> best parameters :"
	for param_name in sorted(parameters.keys()):
		print("\t%s = %r" % (param_name, best_parameters[param_name]))

	"""
#	best parameters :
	activation = 'relu'
	alpha = 1e-06
	tol = 0.0001
	"""
if __name__ == "__main__":
    main()

