import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, accuracy_score, f1_score, confusion_matrix, roc_auc_score, roc_curve
from sklearn.model_selection import train_test_split, StratifiedKFold
from sklearn.datasets import make_classification
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn.linear_model import LogisticRegression, Perceptron
from sklearn import model_selection, metrics
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from matplotlib import pyplot as plt
import seaborn as sns
from tqdm import tqdm
from sklearn.cluster import KMeans
from typing import Tuple
import pandas as pd
import numpy as np
import sys
import umap

from CAC import specificity, sensitivity, best_threshold, predict_clusters, predict_clusters_cac,\
compute_euclidean_distance, calculate_gamma_old, calculate_gamma_new,\
cac, get_new_accuracy, score


datasets = ["adult", "cic", "creditcard", "diabetes",\
            "magic", "sepsis", "titanic"]

# alpha, #clusters
params = {
    "adult": [0.1,2],
    "cic": [0.04,2],
    "creditcard": [0.04,3],
    "diabetes": [2,2],
    "magic": [0.04,2],
    "sepsis": [0.04,5],
    "spambase": [1,2],
    "titanic": [2,2],
}

for DATASET in datasets:
    # DATASET = "creditcard" # see folder, *the Titanic dataset is different*
    print("Testing on Dataset: ", DATASET)

    ############ FOR CIC DATASET ############
    if DATASET == "cic":
        Xa = pd.read_csv("./data/CIC/cic_set_a.csv")
        Xb = pd.read_csv("./data/CIC/cic_set_b.csv")
        Xc = pd.read_csv("./data/CIC/cic_set_c.csv")

        ya = Xa['In-hospital_death']
        yb = Xb['In-hospital_death']
        yc = Xc['In-hospital_death']

        Xa = Xa.drop(columns=['recordid', 'Survival', 'In-hospital_death'])
        Xb = Xb.drop(columns=['recordid', 'Survival', 'In-hospital_death'])
        Xc = Xc.drop(columns=['recordid', 'Survival', 'In-hospital_death'])

        cols = Xa.columns

        scale = StandardScaler()
        Xa = scale.fit_transform(Xa)
        Xb = scale.fit_transform(Xb)
        Xc = scale.fit_transform(Xc)

        Xa = pd.DataFrame(Xa, columns=cols)
        Xb = pd.DataFrame(Xb, columns=cols)
        Xc = pd.DataFrame(Xc, columns=cols)

        Xa = Xa.fillna(0)
        Xb = Xb.fillna(0)
        Xc = Xc.fillna(0)

        X_train = pd.concat([Xa, Xb]).to_numpy()
        y_train = pd.concat([ya, yb]).to_numpy()

        X_test = Xc.to_numpy()
        y_test = yc.to_numpy()

        alpha = params[DATASET][0]
        n_clusters = params[DATASET][1]
        scores = []
        print("Results for base classifier")
        for i in range(5):
            # lr = LogisticRegression()
            lr = RandomForestClassifier(n_estimators=20)
            lr.fit(X_train, y_train)
            preds = lr.predict(X_test)
            pred_proba = lr.predict_proba(X_test)
            print([f1_score(preds, y_test), roc_auc_score(y_test, pred_proba[:,1])])
            print("\n")

        for i in range(5):
            beta = -np.infty # do not change this
            clustering = KMeans(n_clusters=n_clusters, random_state=i, max_iter=300)
            # labels = np.random.randint(0, n_clusters, [len(X_train)])
            labels = clustering.fit(X_train).labels_
            cluster_centers, models, alt_labels, errors, seps, loss = cac(X_train, labels, 10, np.ravel(y_train), alpha, beta, classifier="RF", verbose=True)
            # print(score(X_test, np.array(y_test), models, cluster_centers[1], alt_labels, alpha, flag="old", verbose=True)[1:3])
            f1, auc = score(X_test, np.array(y_test), models, cluster_centers[1], alt_labels, alpha, flag="old", verbose=True)[1:3]
            print("Initial Clustering Score:")
            print("F1: ", f1[0], "AUC: ", auc[0])
            print("\nBest CAC Clustering")
            idx = np.argmax(f1[1:])
            print("F1: ", f1[idx+1], "AUC: ", auc[idx+1])
            print("\n")

    elif DATASET == "titanic":
        X_train = pd.read_csv("./data/" + DATASET + "/" + "X_train.csv").to_numpy()
        X_test = pd.read_csv("./data/" + DATASET + "/" + "X_test.csv").to_numpy()
        y_train = pd.read_csv("./data/" + DATASET + "/" + "y_train.csv").to_numpy()
        y_test = pd.read_csv("./data/" + DATASET + "/" + "y_test.csv").to_numpy()

        alpha = params[DATASET][0]
        n_clusters = params[DATASET][1]
        scores = []
        print("Results for base LR classifier")
        for i in range(5):
            lr = LogisticRegression()
            lr = RandomForestClassifier(n_estimators=20)
            lr.fit(X_train, y_train)
            preds = lr.predict(X_test)
            pred_proba = lr.predict_proba(X_test)
            print([f1_score(preds, y_test), roc_auc_score(y_test, pred_proba[:,1])])
            print("\n")

        for i in range(5):
            beta = -np.infty # do not change this
            clustering = KMeans(n_clusters=n_clusters, random_state=i, max_iter=300)
            labels = np.random.randint(0, n_clusters, [len(X_train)])
            cluster_centers, models, alt_labels, errors, seps, loss = cac(X_train, labels, 10, np.ravel(y_train), alpha, beta, classifier="RF", verbose=True)
            # print(score(X_test, np.array(y_test), models, cluster_centers[1], alt_labels, alpha, flag="old", verbose=True)[1:3])
            f1, auc = score(X_test, np.array(y_test), models, cluster_centers[1], alt_labels, alpha, flag="old", verbose=True)[1:3]
            print("Initial Clustering Score:")
            print("F1: ", f1[0], "AUC: ", auc[0])
            print("\nBest CAC Clustering")
            idx = np.argmax(f1[1:])
            print("F1: ", f1[idx+1], "AUC: ", auc[idx+1])
            print("\n")

    ###########################################

    else:
        X = pd.read_csv("./data/" + DATASET + "/" + "X.csv").to_numpy()
        y = pd.read_csv("./data/" + DATASET + "/" + "y.csv").to_numpy()
        skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=0)
        alpha = params[DATASET][0]
        n_clusters = params[DATASET][1]
        i = 0
        scale = StandardScaler()
        alpha = params[DATASET][0]
        n_clusters = params[DATASET][1]
        scores = []
        print("Training Base LR classifier")

        for train, test in skf.split(X, y):
            i += 1
            lr = LogisticRegression()
            lr = RandomForestClassifier(n_estimators=20)
            print("Iteration: " + str(i))
            X_train, X_test, y_train, y_test = X[train], X[test], y[train], y[test]
            X_train = scale.fit_transform(X_train)
            X_test = scale.fit_transform(X_test)
            lr.fit(X_train, y_train.ravel())
            preds = lr.predict(X_test)
            pred_proba = lr.predict_proba(X_test)
            print("F1: ", f1_score(preds, y_test), "AUC:", roc_auc_score(y_test.ravel(), pred_proba[:,1]))

        print("\nTraining CAC")
        i = 0
        for train, test in skf.split(X, y):
            i += 1
            print("Stratified k-fold partition ", str(i))
            beta = -np.infty # do not change this
            clustering = KMeans(n_clusters=n_clusters, random_state=0, max_iter=300)
            X_train, X_test, y_train, y_test = X[train], X[test], y[train], y[test]
            X_train = scale.fit_transform(X_train)
            X_test = scale.fit_transform(X_test)
            labels = clustering.fit(X_train).labels_
            cluster_centers, models, alt_labels, errors, seps, l1 = cac(X_train, labels, 10, np.ravel(y_train), alpha, beta, classifier="RF", verbose=True)
            f1, auc = score(X_test, np.array(y_test), models, cluster_centers[1], alt_labels, alpha, flag="old", verbose=True)[1:3]
            print("Initial Clustering Score:")
            print("F1: ", f1[0], "AUC: ", auc[0])
            print("\nBest CAC Clustering")
            idx = np.argmax(f1[1:])
            print("F1: ", f1[idx+1], "AUC: ", auc[idx+1])
            print("\n")