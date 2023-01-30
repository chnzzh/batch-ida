import os
import subprocess

from .bi_ida import BI_IDA


def _match_be_files(A_dir: str, B_dir: str) -> list:
    """把A和B文件夹下名称相同的文件配对 （取交集）"""
    A_files = os.listdir(A_dir)
    B_files = os.listdir(B_dir)
    cmp_files = [i for i in A_files if i in B_files]

    pairs = []

    for file in cmp_files:
        a = os.path.join(A_dir, file)
        b = os.path.join(B_dir, file)
        pairs.append((a, b))

    return pairs


class BI_Bindiff(BI_IDA):
    def __init__(self):
        super().__init__()
        self._path_bindiff = ''
        self._path_bindiff_exe = ''

    def _pre_check(self):
        if not os.path.isfile(self._path_bindiff_exe):
            return False
        return True

    def set_bindiff_path(self, bindiff_path: str):
        exe_path = os.path.join(bindiff_path, r'bin\bindiff.exe')
        if os.path.isfile(exe_path):
            self._path_bindiff = bindiff_path
            self._path_bindiff_exe = exe_path
            return True
        return False

    def generate_BinExport(self, idb_dir: str):
        """idb to BinExport，输入为包含idb文件的文件夹"""
        if not self._pre_check():
            raise Exception('Bindiff Pre check failed.')
        if not os.path.isdir(idb_dir):
            raise Exception('Idb dir not exist.')

        export_path = os.path.join(os.path.dirname(idb_dir), os.path.basename(idb_dir) + '_Export')
        if not os.path.isdir(export_path):
            os.mkdir(export_path)

        cmd = [self._path_bindiff_exe, '--export=True', f'--output_dir={export_path}', idb_dir]

        rt = subprocess.Popen(cmd)
        rt.wait()

        return export_path

    def generate_bindiff(self, A_be_file: str, B_be_file: str, output_dir: str):
        """输入比较的两个BinExport文件路径"""
        if not self._pre_check():
            raise Exception('Bindiff Pre check failed.')
        if not (os.path.isfile(A_be_file) | os.path.isfile(B_be_file)):
            raise Exception('BinExport file not exist.')

        if not os.path.isdir(output_dir):
            os.mkdir(output_dir)

        cmd = [self._path_bindiff_exe, f'--output_dir={output_dir}', A_be_file, B_be_file]
        rt = subprocess.Popen(cmd)
        rt.wait()

        return output_dir

    def batch_bindiff(self, A_dir: str, B_dir: str, output_dir: str = None):
        if not (os.path.isdir(A_dir) | os.path.isdir(B_dir)):
            raise Exception('Bin dir not exist.')

        if not output_dir:
            output_dir = os.path.join(os.path.dirname(A_dir), f'{os.path.basename(A_dir)}_vs_{os.path.basename(B_dir)}')
        if not os.path.isdir(output_dir):
            os.mkdir(output_dir)

        # 1. 源文件转化为idb
        A_idb_dir = super().batch_idb_fromdir(A_dir)
        B_idb_dir = super().batch_idb_fromdir(B_dir)
        print('END Step 1')

        # 2. idb转化为Export
        A_export_dir = self.generate_BinExport(A_idb_dir)
        B_export_dir = self.generate_BinExport(B_idb_dir)
        print('END Step 2')

        # 3. Export转化为bindiff
        pairs = _match_be_files(A_export_dir, B_export_dir)
        for pair in pairs:
            bindiff_dir = self.generate_bindiff(pair[0], pair[1], output_dir)
        print('[Finish!]', bindiff_dir)

        return output_dir
