import os
import sqlite3


class BI_SingleAnalyzer:
    def __init__(self, db_file_path):
        self.name = os.path.basename(db_file_path)
        self.path = db_file_path
        self.db = sqlite3.connect(db_file_path)
        self.similarity = self.select_similarity()
        self.diff_func = self.select_diff_func()

    def select_similarity(self):
        cu = self.db.cursor()
        cu.execute("select similarity from metadata;")
        return cu.fetchall()[0][0]

    def select_diff_func(self):
        cu = self.db.cursor()
        cu.execute("select * from function where similarity < 1;")
        ans = cu.fetchall()
        return ans

    def print_base_info(self):
        print(self.similarity, end='\t')
        print(len(self.diff_func), end='\t')

        cu = self.db.cursor()
        cu.execute("select functions from file;")
        ans = cu.fetchall()
        func = ans[0][0] - ans[1][0]
        cu.execute("select libfunctions from file;")
        ans = cu.fetchall()
        libfunc = ans[0][0] - ans[1][0]

        print(func, end='\t')
        print(libfunc, end='\t')
        print(self.name, end='\t')
        print()
