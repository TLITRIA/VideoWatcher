from DataAccess.DataBase import *
from DataAccess.sql_query import *
from os.path import abspath
from Common.Logger import *

"""
测试DataAccess模块
"""

from pprint import pprint

def test_db():
    db = DataBase()
    db.Connect(videowatcher_sql_fp)

    with timeblock("get_unfill_up_id"):
        print("get_unfill_up_id")
        pprint(get_unfill_up_id(db))


    with timeblock("get_up_id_whichvideoisnotnew"):
        print("get_up_id_whichvideoisnotnew")
        pprint(get_up_id_whichvideoisnotnew(db))