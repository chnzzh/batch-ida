import os

from .bi_singleanalyzer import BI_SingleAnalyzer


class BI_Analyzer:
    def __init__(self, db_path):
        """
        [Not Recommend to Use]
        BI_Analyzer used to read .BinDiff files in dir db_path.
        """
        self.db_path = db_path
        self.analyzers = []

        # 读入数据库
        self.input_all_bindiff_db()

    def input_all_bindiff_db(self):
        for file in os.listdir(self.db_path):
            self.analyzers.append(BI_SingleAnalyzer(os.path.join(self.db_path, file)))

    def print_base_info(self):
        for i in self.analyzers:
            i.print_base_info()
