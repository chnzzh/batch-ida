import os
import sqlite3


class BI_SingleAnalyzer:
    def __init__(self, db_file_path):
        self.name = os.path.basename(db_file_path)
        self.path = db_file_path
        self.db = sqlite3.connect(db_file_path)
        self.similarity = float(self.select_similarity())
        self.confidence = float(self.select_confidence())
        self.diff_func = self.select_diff_func()

    def select_similarity(self):
        cu = self.db.cursor()
        cu.execute("select similarity from metadata;")
        return cu.fetchall()[0][0]

    def select_confidence(self):
        cu = self.db.cursor()
        cu.execute("select confidence from metadata;")
        return cu.fetchall()[0][0]

    def select_diff_func(self):
        cu = self.db.cursor()
        cu.execute("select * from function where similarity < 1;")
        ans = cu.fetchall()
        return ans

    def print_base_info(self):
        base_info = self.get_base_info_dict()
        for i in base_info.values():
            print(i, end='\t')
        print()

    def get_base_info_dict(self):
        cu = self.db.cursor()
        cu.execute("select functions from file;")
        ans = cu.fetchall()
        func_dif = ans[0][0] - ans[1][0]
        cu.execute("select libfunctions from file;")
        ans = cu.fetchall()
        libfunc = ans[0][0] - ans[1][0]
        rt = dict(similarity=self.similarity, confidence=self.confidence, total_func=len(self.diff_func),
                  func_dif=func_dif, libfunc_dif=libfunc, name=self.name)
        return rt
