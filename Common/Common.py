import os, sys
import subprocess
import hashlib
import random
from ipdb import set_trace as ist


def g_chdir_byfp(__filepath: str):
    os.chdir(os.path.dirname(__filepath))


def g_mkdir_byfp(__filepath: str):
    os.makedirs(os.path.dirname(__filepath), exist_ok=True)


def runcmdlist(cmdlist: list):
    try:
        result = subprocess.run(cmdlist, shell=True, stdout=sys.stdout, stderr=sys.stderr, text=True)
        return result
    except Exception as e:
        print(e)


# 处理中文字符
from urllib.parse import unquote


def get_file_hash(file_path, hash_method=hashlib.sha256, block_size=65536):
    h = hash_method()
    with open(file_path, "rb") as f:
        while chunk := f.read(block_size):
            h.update(chunk)
    return h.hexdigest()


def split_list(lst, n):
    return (lst[i::n] for i in range(n))


def scan_foldsize(folder_path):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(folder_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size