import os
import logging
from filecmp import dircmp

def file_filter(file):
    return 1

class BI_Dircmp:
    def __init__(self, dir_a: str, dir_b: str, dst_a: str, dst_b: str):
        """
        BI_Dircmp compares files in dir_a & dir_b, and remove the different files to dst;
        :param dir_a: Source directory A
        :param dir_b: Source directory B
        :param dst_a: An empty directory to save the diff files in dir_a
        :param dst_b: An empty directory to save the diff files in dir_b
        """
        self.dir_a = os.path.expanduser(dir_a)
        self.dir_b = os.path.expanduser(dir_b)

        self.dst_a = ''
        self.dst_b = ''

        self.set_copyto_dir(dst_a, dst_b)
        self.file_filter = file_filter

    def _print_diff_files(self, dcmp, layer, file_fliter):
        try:
            lo = list(filter(file_fliter, dcmp.left_only))
            ro = list(filter(file_fliter, dcmp.right_only))
            df = list(filter(file_fliter, dcmp.diff_files))
            ff = list(filter(file_fliter, dcmp.funny_files))
        except PermissionError as e:
            logging.error(f"[Dircmp] Check Permission: {e}")
            return

        if len(lo) | len(ro) | len(df) | len(ff):
            logging.info('[Dircmp] '+ '--' * layer + f"{dcmp.left} {dcmp.right}")

        if len(df):
            import shutil
            for file in df:
                shutil.copy2(os.path.join(dcmp.left, file), self.dst_a)
                shutil.copy2(os.path.join(dcmp.right, file), self.dst_b)
            logging.info('[Dircmp] \033[1;35m' + '  ' * layer + f"diff files: {df}" + '\033[0m')

        if len(lo):
            logging.info('[Dircmp] \033[1;34m' + '  ' * layer + f"left_only: {lo}" + '\033[0m')

        if len(ro):
            logging.info('[Dircmp] \033[1;32m' + '  ' * layer + f"right_only: {ro}" + '\033[0m')

        if len(ff):
            logging.info('[Dircmp] \033[1;31m' + '  ' * layer + f"funny: {ff}" + '\033[0m')

        for sub_dcmp in dcmp.subdirs.values():
            self._print_diff_files(sub_dcmp, layer + 1, self.file_filter)

    def set_copyto_dir(self, dst_a: str, dst_b: str):
        dst_a = os.path.expanduser(dst_a)
        dst_b = os.path.expanduser(dst_b)

        if not os.path.isdir(dst_a):
            os.mkdir(dst_a)
        if not os.path.isdir(dst_b):
            os.mkdir(dst_b)

        self.dst_a = dst_a
        self.dst_b = dst_b

    def cmp(self):
        dcmp = dircmp(self.dir_a, self.dir_b)
        self._print_diff_files(dcmp, 0, self.file_filter)
