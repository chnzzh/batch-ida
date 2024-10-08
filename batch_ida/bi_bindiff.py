import os
import subprocess
import logging

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
    def __init__(self, bindiff_path: str = ''):
        super().__init__()
        self._path_bindiff = ''
        self._path_bindiff_exe = ''

        self.set_bindiff_path(bindiff_path)

    def _pre_check(self):
        if not os.path.isfile(self._path_bindiff_exe):
            return False
        return True

    def set_bindiff_path(self, bindiff_path: str):
        """
        To set the path of BinDiff.
        for example:
            Windows: set_bindiff_path(r'C:\Program Files\BinDiff')
            Linux  : set_bindiff_path('/usr/local/bin')
        """
        exe_path = os.path.join(bindiff_path, 'bin', 'bindiff.exe') if os.name == 'nt' else os.path.join(bindiff_path, 'bindiff')
        if os.path.isfile(exe_path):
            self._path_bindiff = bindiff_path
            self._path_bindiff_exe = exe_path
            return True
        return False

    def generate_BinExport(self, idb_dir: str):
        """
        To generate BinExport from idb files.
        """
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
        """
        To generate BinDiff Database from BinExport files.
        """
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
        """
        To batch compare two directories of binary files.
        for example: output = bib.batch_bindiff(dst_a, dst_b)
        """
        if not (os.path.isdir(A_dir) | os.path.isdir(B_dir)):
            raise Exception('Bin dir not exist.')

        if not output_dir:
            output_dir = os.path.join(os.path.dirname(A_dir), f'{os.path.basename(A_dir)}_vs_{os.path.basename(B_dir)}')
        if not os.path.isdir(output_dir):
            os.mkdir(output_dir)

        # 1. 源文件转化为idb
        A_idb_dir = super().batch_idb_fromdir(A_dir)
        B_idb_dir = super().batch_idb_fromdir(B_dir)
        logging.info('END Step 1')

        # 2. idb转化为Export
        A_export_dir = self.generate_BinExport(A_idb_dir)
        B_export_dir = self.generate_BinExport(B_idb_dir)
        logging.info('END Step 2')

        # 3. Export转化为bindiff
        pairs = _match_be_files(A_export_dir, B_export_dir)
        bindiff_dir = output_dir
        for pair in pairs:
            bindiff_dir = self.generate_bindiff(pair[0], pair[1], output_dir)
        logging.info(f'[Bindiff] Finish! Output in {bindiff_dir}')

        return output_dir
