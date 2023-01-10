import os
import subprocess
import shutil

class BI_IDA:
    def __init__(self):
        self._path_ida = ''
        self._path_ida_exe = ''
        self._filter = ['.asm', '.idb']
        self.max_subprocess = 16

    def _pre_check(self):
        if not os.path.isfile(self._path_ida_exe):
            return False
        return True

    def set_ida_path(self, ida_path: str):
        exe_path = os.path.join(ida_path, 'ida.exe')
        if os.path.isfile(exe_path):
            self._path_ida = ida_path
            self._path_ida_exe = exe_path
            return True
        return False

    def generate_idb(self, file_path):
        """
        通过ida从二进制生成idb文件，注意是在当前目录下
        :param file_path: 文件路径
        :return:
        """
        if not self._pre_check():
            raise Exception('IDA Pre check failed.')
        if not os.path.isfile(file_path):
            raise Exception('File not exist.')

        # 如果已经解析过，直接跳过
        if os.path.isfile(file_path+'.idb'):
            return None

        rt = subprocess.Popen([self._path_ida_exe, '-B', file_path])
        return rt


    def batch_idb_fromdir(self, bin_dir: str, output_dir: str = None):
        """
        批量处理文件夹内的二进制文件, 处理结果复制到output_dir，开多进程加速处理
        :param bin_dir:
        :param output_dir:
        :return:
        """
        if not os.path.isdir(bin_dir):
            raise Exception('Bin directory not exist.')
        if not output_dir:
            output_dir = os.path.join(os.path.dirname(bin_dir), os.path.basename(bin_dir) + '_IDB')
        if not os.path.isdir(output_dir):
            os.mkdir(output_dir)

        pool = []
        index = 0

        for maindir, subdir, file_name_list in os.walk(bin_dir):
            max_len = len(file_name_list)
            for file in file_name_list:
                file_path = os.path.join(maindir, file)

                if os.path.splitext(file_path)[1] in self._filter:
                    index = index + 1
                    continue

                while len(pool) >= self.max_subprocess:
                    for i in pool:
                        if i[0] is None:
                            shutil.copy2(i[1], output_dir)
                            pool.remove(i)
                            index = index + 1
                            print(f'({index}/{max_len}) [IDA]', i[1])
                        elif i[0].poll() is not None:
                            shutil.copy2(i[1], output_dir)
                            pool.remove(i)
                            index = index + 1
                            print(f'({index}/{max_len}) [IDA]', i[1])

                proc = self.generate_idb(file_path)
                idb_path = os.path.join(bin_dir, file + '.idb')
                pool.append((proc, idb_path))

        while len(pool) > 0:
            for i in pool:
                if i[0] is None:  # 已存在
                    shutil.copy2(i[1], output_dir)
                    pool.remove(i)
                    index = index + 1
                    print(f'({index}/{max_len})[IDA]', i[1])
                elif i[0].poll() is not None:
                    shutil.copy2(i[1], output_dir)
                    pool.remove(i)
                    index = index + 1
                    print(f'({index}/{max_len})[IDA]', i[1])

        return output_dir
