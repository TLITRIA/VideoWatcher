import os, sys
import shutil
from Common.Common import runcmdlist

fold = R"E:\VideoWatcher\UI"
pyuic6 = R"E:\VideoWatcher\.VideoWatcher\Scripts\pyuic6.exe"


def searchUIFile(fold):
    ret = []
    for entry, folds, files in os.walk(fold):
        for file in files:
            if file.endswith(".ui"):
                ret.append(os.path.join(entry, file))
        for fold in folds:
            ret += searchUIFile(os.path.join(entry, fold))
    return list(set(ret))


def searchPyFile(fold):
    ret = []
    for entry, folds, files in os.walk(fold):
        for file in files:
            if file.endswith(".py"):
                ret.append(os.path.join(entry, file))
        for fold in folds:
            ret += searchPyFile(os.path.join(entry, fold))
    return list(set(ret))


for file in searchPyFile(fold):
    os.remove(file)
for file in searchUIFile(fold):
    cmdlist = [pyuic6, file, "-o", file.split(".ui")[0] + ".py"]
    runcmdlist(cmdlist)
