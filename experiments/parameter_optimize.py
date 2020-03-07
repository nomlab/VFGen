import os
import sys
import yaml
import datetime
import csv
import numpy as np
import pandas as pd
from skopt import gp_minimize
from skopt.plots import plot_convergence
from skopt import BayesSearchCV
from skopt.space import Real, Categorical, Integer
import matplotlib.pyplot as plt
app_home = os.path.abspath(os.path.join( os.path.dirname(os.path.abspath(__file__)) , ".." ))
sys.path.append(os.path.join(app_home,"lib"))
from AccessLogAnalyzer import *
from WDEstimator import *

# 設定ファイルのロード
try:
    settings = yaml.load(open(app_home + '/settings.yml','r'), Loader=yaml.SafeLoader)
except:
    print("Error: Cannnot open log file. Check your settings.")
    sys.exit()

logfile = settings["ACCESS_LOG_FILE_PATH"]

try:
    print("Loading", flush=True)
    logs = LogParser(sep=",")
    if os.path.exists(app_home + "/log.pickle"):
        logs.load()
        logs.update(logfile)
        logs.dump()
    else:
        logs.parse(logfile)
        logs.dump()
    print("Loaded",len(logs.log),"logs")
except:
    print("Error: Failed to load log dump data. ")
    sys.exit()

records = logs.log.op_filter(["Created", "Updated"])
## train_record: パラメータ最適化のための学習データ（アクセス履歴）
train_record = records.time_filter(datetime.datetime(2019,9,5), datetime.datetime(2019,9,19))
## answer_set: ワーキングディレクトリの正解データ．train_recordの期間の正解データが入っていることが条件．
##             CSV形式で，以下の形式
##             ワーキングディレクトリの絶対パス,作業名
answer_set = "/home/ryota/Project/research/MarkWD/working_directories.csv"

print("N of train data: ",len(train_record))

def make_weight(start, dec):
    w = [start]
    while(True):
        n = w[-1]*((100-dec)*0.01)
        if n < 1:
            w.append(1)
            break
        else:
            w.append(n)
    return w

def f(x):
    weight = [p for p in range(x[0],1,-x[1])] + [1]
    #weight = make_weight(x[0],x[1])
    move_threshold = x[2]
    density_threshold = x[3] / 100

    print("weight:", weight)
    print("move_threshold", move_threshold)
    print("density_threshold", density_threshold)
    
    dirlist = []
    worklist = []
    with open(answer_set) as f:
        reader = csv.reader(f)
        for row in reader:
            dirlist.append(row[0])
            worklist.append(row[1])

    wdlist_in_logs = []
    #print("----------answer set----------")
    for d in dirlist:
        if len(train_record.path_filter(d)) > 0:
            wdlist_in_logs.append(d)
    #        print(d)

    # WD推定
    wd = WDEstimator(train_record, weight, move_threshold, density_threshold)
    estimated_wd = wd.workingdir

    match_wd = []
    not_match_wd = []
    print("----------match----------")
    for wl in wdlist_in_logs:
        if wl in estimated_wd:
            match_wd.append(wl)
            print(wl)
        else:
            not_match_wd.append(wl)

    print("----------not_match----------")
    for nw in not_match_wd:
        print(nw)

    print("----------statistic----------")
    wd_c = len(wdlist_in_logs)
    wd_d = len(estimated_wd)
    c_and_d = len(match_wd)
    print("                  WD_correct : ", str(wd_c))
    print("               WD_discovered : ", str(wd_d))
    print("WD_correct AND WD_discovered : ", str(c_and_d))
    print("------------score------------")
    print("                   Precision : ", str(c_and_d/wd_d))
    print("                      Recall : ", str(c_and_d/wd_c))
    pre = c_and_d/wd_d
    rec = c_and_d/wd_c
    try:
        fmeasure = 2 / ((pre**-1) + (rec**-1))
    except:
        fmeasure = 0.0
    print("                   F-measure : ", str(fmeasure))

    return -1 * fmeasure

def main():
    ## 探索範囲
    spaces = [
        (14, 16), # start
        (3, 5), # decrease,
        (26, 28), # move_threshold
        (50, 120) # density_threshold
        #['linear', 'poly', 'rbf']
    ]

    res = gp_minimize(
        f, spaces,
        acq_func="EI",
        n_calls=30)

    print(res.fun)
    print(res.x)

    fig, ax = plt.subplots()
    plot_convergence(res, ax=ax)
    plt.savefig("convergence_plot.pdf")
    
if __name__ == "__main__":
    main()
