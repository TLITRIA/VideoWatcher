import os, sys
import sqlite3
import pandas as pd
import traceback
from Pattern.singleton import singleton
from Common.Common import *
from Common.Abspath import default_db_fp
from sqlalchemy import create_engine

@singleton
class DataBase:
    isConnected = False
    db_fp = ""

    def __init__(self):
        pass

    def __del__(self):
        self.Disconnect()

    def Connect(self, db_fp=default_db_fp):
        if not os.path.exists(db_fp):
            g_mkdir_byfp(db_fp)
        if self.isConnected and self.conn:
            self.conn.close()
        try:
            self.conn = sqlite3.connect(db_fp)
            self.isConnected = True
            self.db_fp = db_fp
        except sqlite3.Error as e:
            print(e)
            self.isConnected = False

    def Disconnect(self):
        if self.isConnected and self.conn:
            self.conn.close()
            self.isConnected = False

    def ExecuteNow(self, sql: str):
        if self.isConnected and self.conn:
            # TODO 加锁
            try:
                self.conn.execute(sql)
                self.conn.commit()
            except sqlite3.Error as e:
                print(e)
                print(sql)

    def Query2DF(self, sql: str):
        if self.isConnected and self.conn:
            return pd.read_sql(sql, self.conn)

    def DF2DB(self, df: pd.DataFrame, table_name: str):
        if self.isConnected and self.conn:
            df.to_sql(table_name, self.conn, if_exists="replace", index=False)

    def ReadTable(self, table_name: str):
        if self.isConnected and self.conn:
            return pd.read_sql(f"SELECT * FROM {table_name}", self.conn)



def df2sqlite_replace(df: pd.DataFrame, sqlite_fp: str, sheetname: str = "untitled"):
    sqlite_engine = create_engine("sqlite:///" + sqlite_fp)
    df.to_sql(sheetname, con=sqlite_engine, if_exists="replace", index=False)


def df2sqlite_update(
    df: pd.DataFrame, sqlite_fp: str, drop_tags=[], sheetname: str = "untitled"
):
    existed_df = sqlite2df(sqlite_fp, f"SELECT * FROM {sheetname};")
    if existed_df.shape[0]:
        df = pd.concat([existed_df, df], ignore_index=True)
    df.drop_duplicates(subset=drop_tags, keep="last", inplace=True)
    sqlite_engine = create_engine("sqlite:///" + sqlite_fp)
    df.to_sql(sheetname, con=sqlite_engine, if_exists="replace", index=False)


def sqlite2df(sqlite_fp: str, sql: str = "") -> pd.DataFrame:
    df = pd.DataFrame()
    if not os.path.exists(sqlite_fp):
        return df
    if not sql:
        sql = "SELECT * FROM untitled;"
    sqlite_engine = create_engine("sqlite:///" + sqlite_fp)
    try:
        with sqlite_engine.connect() as conn, conn.begin():
            df = pd.read_sql_query(sql, conn)
    except:
        traceback.print_exc()
    return df
