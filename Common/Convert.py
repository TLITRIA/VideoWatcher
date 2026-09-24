import json
import os


def abspath(filepath: str) -> str:
    return os.path.abspath(filepath)


def savejson(filepath: str, data):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)  # human readable


def readjson(filepath: str):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def savehtml(filepath: str, htmlsrc):
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(htmlsrc)


def biliurl2BV(certain_url):
    return certain_url[31:43]
    return certain_url.split("/")[-1].split("?")[0]


def BV2url(bv):
    return f"https://www.bilibili.com/video/{bv}"
