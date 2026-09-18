import os, sys
import sqlite3
import pandas as pd

from Pattern.singleton import singleton
from Common.Common import *

@singleton
class DataBase:
    isConnected = False
    db_fp = ''
    def __init__(self):
        pass
    def __del__(self):
        self.Disconnect()

    def Connect(self, db_fp):
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

    def ExecuteNow(self, sql:str):
        if self.isConnected and self.conn:
            # TODO 加锁
            try:
                self.conn.execute(sql)
                self.conn.commit()
            except sqlite3.Error as e:
                print(e)
                print(sql)

    def Query2DF(self, sql:str):
        if self.isConnected and self.conn:
            return pd.read_sql(sql, self.conn)

    def DF2DB(self, df:pd.DataFrame, table_name:str):
        if self.isConnected and self.conn:
            df.to_sql(table_name, self.conn, if_exists='replace', index=False)

    def ReadTable(self, table_name:str):
        if self.isConnected and self.conn:
            return pd.read_sql(f'SELECT * FROM {table_name}', self.conn)
            