# 1. BI_Dircmp比较原文件夹，并复制哈希不同的文件到目标文件夹
from batch_ida import BI_Dircmp

# 原始文件夹dirA，dirB，包含需要比较的二进制
dirA = r'\\wsl.localhost\Ubuntu-22.04\home\zzh\fw_project/d9_idrac/_5.00.10.20.d9.extracted/squashfs-root/usr/lib/'
dirB = r'\\wsl.localhost\Ubuntu-22.04\home\zzh\fw_project/d9_idrac/_5.00.20.00.d9.extracted/squashfs-root/usr/lib/'

# 目标文件夹dstA，dstB，用来存放哈希值不同的二进制，是空文件夹
dst_a = r'C:\Users\zzhihan\Desktop\36347\1020'
dst_b = r'C:\Users\zzhihan\Desktop\36347\2000'

# 使用Dircmp比较两个文件夹中文件的差异，并将哈希不同的文件复制到目标文件夹
bid = BI_Dircmp(dirA, dirB, dst_a, dst_b)
bid.cmp()

##################################################################################################
# 使用Bindiff批量分析二进制文件
from batch_ida import BI_Bindiff

bib = BI_Bindiff()

# 设置ida和bindiff路径
bib.set_ida_path('C:\Tools\IDA Pro')
bib.set_bindiff_path('C:\Program Files\BinDiff')
bib.max_subprocess = 16

# 开始比较，结果输出到output文件夹，批量生成idb比较慢
output = bib.batch_bindiff(dst_a, dst_b)

##################################################################################################
# 使用Analyzer批量读输出的Bindiff文件，其实就是sqlite3数据库文件
from batch_ida import BI_Analyzer

bia = BI_Analyzer(r'C:\Users\zzhihan\Desktop\test\4_4010_vs_4_4040')
bia.print_base_info()

"""
依次输出相似度、不同函数个数、ab自身函数的数量差、ab引用函数的数量差，文件名字
"""
