from filecmp import dircmp
import os


def file_filter(file):
    return 1


class BI_Dircmp:
    def __init__(self, dir_a: str, dir_b: str, dst_a: str, dst_b: str):
        self.dir_a = dir_a
        self.dir_b = dir_b

        self.dst_a = ''
        self.dst_b = ''

        self.set_copyto_dir(dst_a, dst_b)
        self.file_filter = file_filter

    def _print_diff_files(self, dcmp, layer, file_fliter):
        lo = list(filter(file_fliter, dcmp.left_only))
        ro = list(filter(file_fliter, dcmp.right_only))
        df = list(filter(file_fliter, dcmp.diff_files))
        ff = list(filter(file_fliter, dcmp.funny_files))

        if len(lo) | len(ro) | len(df) | len(ff):
            print('  ' * layer, dcmp.left, dcmp.right)

        if len(df):
            import shutil
            for file in df:
                shutil.copy2(os.path.join(dcmp.left, file), self.dst_a)
                shutil.copy2(os.path.join(dcmp.right, file), self.dst_b)
            print('\033[1;35m', '  ' * layer, 'diff files: ', df, '\033[0m')

        if len(lo):
            print('\033[1;34m', '  ' * layer, 'left_only: ', lo, '\033[0m')

        if len(ro):
            print('\033[1;32m', '  ' * layer, 'right_only: ', ro, '\033[0m')

        if len(ff):
            print('\033[1;31m', '  ' * layer, 'funny: ', ff, '\033[0m')

        for sub_dcmp in dcmp.subdirs.values():
            self._print_diff_files(sub_dcmp, layer + 1)

    def set_copyto_dir(self, dst_a: str, dst_b: str):
        if not os.path.isdir(dst_a):
            os.mkdir(dst_a)
        if not os.path.isdir(dst_b):
            os.mkdir(dst_b)

        self.dst_a = dst_a
        self.dst_b = dst_b

    def cmp(self):
        dcmp = dircmp(self.dir_a, self.dir_b)
        self._print_diff_files(dcmp, 0, self.file_filter)



