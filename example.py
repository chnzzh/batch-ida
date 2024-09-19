# Description: An example script to show how to use the batch_ida module

#=============================================================================#
# 0. generate idb files from binary files on Windows
from batch_ida import BI_IDA

bi = BI_IDA()
bi.set_ida_path(r'C:\Tools\IDA Pro')

# bi.set_script(r'.\example_script.py') # optional
bi.batch_idb_fromdir(r'.\path\to\binary_files_dir')

#=============================================================================#
# 1. compare two directories and copy different files to dst_a and dst_b
from batch_ida import BI_Dircmp

# dirA, dirB are directories containing binary files to compare, e.g. rootfs
dirA = r'\path\to\dirA'
dirB = r'\path\to\dirB'

# dst_a, dst_b are empty directories to store different files, will be created if not exist
dst_a = r'\path\to\dst_a'
dst_b = r'\path\to\dst_b'

# compare two directories and copy different files
bid = BI_Dircmp(dirA, dirB, dst_a, dst_b)
bid.cmp()

#=============================================================================#
# 2. batch compare two directories of binary files
from batch_ida import BI_Bindiff

bib = BI_Bindiff()
bib.set_ida_path(r'path\to\IDA_Pro')
bib.set_bindiff_path(r'C:\Program Files\BinDiff')
bib.max_subprocess = 16

output_dir_path = bib.batch_bindiff(dst_a, dst_b)

#=============================================================================#
# 3. analyze the output of BinDiff, or you can use other sqlite3 tool to read the database

from batch_ida import BI_Analyzer
bia = BI_Analyzer(r'path\to\output_dir')
bia.print_base_info()

# let's print the diff files with similarity < 0.95 and != 0.0
print("%s\t%s\t%s\t%s\t%s\t%s" % ("SIM", "CONF", "TOTAL", "FUNC", "LIBFUNC", "NAME"))

info_list = bia.get_info_list()
for i in info_list:
    if i['total_func'] & i['func_dif'] & i['libfunc_dif']:
        print("%.02f\t%.2f\t%d\t%d\t%d\t%s" % (i['similarity'], i['confidence'], i['total_func'], i['func_dif'], i[
            "libfunc_dif"], i['name']))
    elif i['similarity'] < 0.95 and i['similarity'] != 0.0:
        print("%.02f\t%.2f\t%d\t%d\t%d\t%s" % (i['similarity'], i['confidence'], i['total_func'], i['func_dif'], i[
            "libfunc_dif"], i['name']))
