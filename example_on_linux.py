# Description: Example of using wine to run batch_ida on linux

#=============================================================================#
# 0. generate idb files from binary files, with wine on linux
import os
from batch_ida import BI_IDA

os.environ["WINEDEBUG"] = "-all"    # don't show the annoying wine debug info

bi = BI_IDA(ida_path="/path/to/IDA_Pro_dir", use_wine=True)
bi.max_subprocess = 8
bi.batch_idb_fromdir(r"/path/to/binary_files_dir")

#=============================================================================#
# 1. compare two directories and copy different files
from batch_ida import BI_Dircmp

dirA = r'/path/to/dirA'
dirB = r'/path/to/dirB'

# dst_a, dst_b are empty directories to store different files, will be created if not exist
dst_a = r'/path/to/dst_a'
dst_b = r'/path/to/dst_b'

# compare two directories and copy different files
bid = BI_Dircmp(dirA, dirB, dst_a, dst_b)
bid.cmp()

#=============================================================================#
# 2. batch compare two directories of binary files

# todo: wine bindiff on linux
