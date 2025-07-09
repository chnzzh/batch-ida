import os
import shutil
import subprocess
import struct
import logging
import sys


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)-7s | %(message)s')

# Automatically detects the architecture for PE files
def detect_arch_pe_files(filename):
    IMAGE_FILE_MACHINE_I386 = 0x014c
    IMAGE_FILE_MACHINE_IA64 = 0x0200
    IMAGE_FILE_MACHINE_AMD64 = 0x8664
    IMAGE_FILE_MACHINE_ARMTHUMB_MIXED = 0x01c2
    IMAGE_FILE_MACHINE_ARM64 = 0xAA64

    with open(filename, "rb") as f:
        f.seek(60)
        s = f.read(4)
        header_offset = struct.unpack("<L", s)[0]
        f.seek(header_offset + 4)
        s = f.read(2)
        machine = struct.unpack("<H", s)[0]
        if machine == IMAGE_FILE_MACHINE_I386 or machine == IMAGE_FILE_MACHINE_ARMTHUMB_MIXED:
            arch = 32
        elif machine == IMAGE_FILE_MACHINE_IA64 or machine == IMAGE_FILE_MACHINE_AMD64 or machine == IMAGE_FILE_MACHINE_ARM64:
            arch = 64
        else:
            arch = None

    return arch


# Automatically detects the architecture for ELF files
def detect_arch_elf_files(filename):
    arch = None
    with open(filename, "rb") as f:
        f.seek(4)
        s = f.read(1)
        if s == b"\x01":
            arch = 32
        elif s == b"\x02":
            arch = 64
        else:
            arch = None

    return arch


def detect_arch(filename):
    with open(filename, "rb") as f:
        pe = f.read(2)
        f.seek(0)
        elf = f.read(4)
    if pe == b"MZ":
        arch = detect_arch_pe_files(filename)
    elif elf == b"\x7fELF":
        arch = detect_arch_elf_files(filename)
    else:
        arch = None
    return arch


class BI_IDA:
    def __init__(self, ida_path: str = '', use_wine: bool = False):
        self._path_ida = ''
        self._path_ida_exe = ''
        self._path_ida64_exe = ''
        self._current_ida_exe = ''
        self._filter = ['.asm', '.idb', '.i64', '.til', '.nam', '.id0', '.id1', '.id2', '.json', '.log', '.dmp']
        self.max_subprocess = 4  # max subprocess num
        self.cmd = ['-B']
        self.use_wine = use_wine

        self._ida_ge90 = False

        if ida_path:
            self.set_ida_path(ida_path)

        if use_wine and not shutil.which('wine'):
            raise Exception('Wine not found.')

    def _pre_check(self):
        if not os.path.isfile(self._path_ida_exe):
            return False
        return True

    def set_script(self, script_path: str):
        script_path = os.path.expanduser(script_path)
        if os.path.isfile(script_path):
            self.cmd = ['-c', '-A', f'-S"{os.path.abspath(script_path)}"']
        else:
            raise Exception('Script not exist.')

    def set_ida_path(self, ida_path: str):
        ida_path = os.path.expanduser(ida_path)
        if sys.platform.startswith('win'):
            exe_name = 'ida.exe'
            exe64_name = 'ida64.exe'
        elif sys.platform.startswith('darwin'):
            exe_name = 'ida'
            exe64_name = 'ida64'
            if ida_path.endswith('.app'):
                ida_path = os.path.join(ida_path, 'Contents', 'MacOS')
        else:
            exe_name = 'ida'
            exe64_name = 'ida64'

        exe_path = os.path.join(ida_path, exe_name)
        exe64_path = os.path.join(ida_path, exe64_name)

        # check if the path is valid
        if os.path.isfile(exe_path):
            self._path_ida = ida_path
            self._path_ida_exe = exe_path
            # check if the 64-bit version exists (noexist > 9.0)
            if os.path.isfile(exe64_path):
                self._path_ida64_exe = exe64_path
            else:
                self._path_ida64_exe = exe_path
                self._ida_ge90 = True
            return True
        return False

    def generate_idb(self, file_path):
        """
        通过ida从二进制生成idb文件，注意是在当前目录下
        :param file_path: 文件路径
        :return:
        """
        file_path = os.path.expanduser(file_path)
        if not self._pre_check():
            raise Exception('IDA Pre check failed: ' + self._path_ida_exe + ' not exist.')
        if not os.path.isfile(file_path):
            raise Exception('File not exist.')

        arch = detect_arch(file_path)
        if arch == 32:
            cmd = [self._path_ida_exe] + self.cmd + [file_path]
        elif arch == 64:
            cmd = [self._path_ida64_exe] + self.cmd + [file_path]
        else:
            #logging.warning(f'Unknown arch, Skip: {file_path}')
            return None

        if self.use_wine:
            cmd = ['wine'] + cmd

        rt = subprocess.Popen(cmd)
        # logging.info(cmd)
        return rt

    def batch_idb_fromdir(self, bin_dir: str, output_dir: str = None, enable_copy: bool = True):
        """
        To generate idb files from binary files in the directory.
        :param bin_dir: The directory of binary files
        :param output_dir: The directory to save the idb files
        :param enable_copy: If True, the idb files will be copied to the output_dir
        :return: The directory of idb files. If output_dir is None and enable_copy is True, the directory will be created.
        """
        bin_dir = os.path.expanduser(bin_dir)
        if output_dir:
            output_dir = os.path.expanduser(output_dir)
        if not os.path.isdir(bin_dir):
            raise Exception('Bin directory not exist.')
        if not output_dir:
            output_dir = os.path.join(os.path.dirname(bin_dir), os.path.basename(bin_dir) + '_IDB')
        if not os.path.isdir(output_dir) and enable_copy:
            os.mkdir(output_dir)

        pool = []
        index = 0
        err_list = []

        def _loop_pool(_index):
            items_to_remove = []
            for i in pool:
                if i[0].poll() is not None:
                    if not (os.path.isfile(i[1]+'.idb') or os.path.isfile(i[1]+'.i64')) :
                        err_list.append(i[1])
                    elif enable_copy:
                        shutil.copy2(i[1], output_dir)
                    items_to_remove.append(i)
                    _index = _index + 1
                    logging.info(f'[IDA] ({index+1}/{max_len}) Success: {i[1]}')
            for i in items_to_remove:
                pool.remove(i)
            return _index

        for maindir, subdir, file_name_list in os.walk(bin_dir):
            max_len = len(file_name_list)

            for file in file_name_list:
                file_path = os.path.join(maindir, file)

                if os.path.splitext(file_path)[1] in self._filter:
                    index = index + 1
                    logging.info(f'[IDA] ({index}/{max_len}) Ignore: {file_path}')
                    continue

                while len(pool) >= self.max_subprocess:
                    index = _loop_pool(index)

                arch = detect_arch(file_path)
                if arch in [32, 64]:
                    idb_path = os.path.join(bin_dir, file)
                else:
                    index = index + 1
                    logging.warning(f'[IDA] ({index}/{max_len}) Unknown: {file_path}')
                    continue

                proc = self.generate_idb(file_path)
                pool.append((proc, idb_path))

            while len(pool) > 0:
                index = _loop_pool(index)

        if len(err_list) > 0:
            logging.error(f'[IDA] Generate {len(err_list)} idb/i64 Failed:')
            for i in err_list:
                logging.error(i)

        return output_dir
