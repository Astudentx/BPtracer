import os
import sys

"""
Central configuration module for BP-Tracer.

该模块主要职责：
1. 定义主程序和资源的路径（主脚本、bin、数据库等）；
2. 定义各类软件的调用路径及默认参数；
3. 定义功能基因、Kraken2 和 HGT 等数据库路径；
4. 提供少量设置函数（如输出路径、数据库选择）。

注意：模块在 import 时会给出一套“默认配置”，
下游可调用 set_output_path / set_kraken2_database / set_HGT_database 动态修改。
"""


"""Default values for filenames and common constants."""
# ====================== 路径配置 ======================
# 主程序所在的上级目录，例如：/path/to/BPtracer/
MAIN_SCRIPT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))  # 指向上一级目录
# 主程序路径（一般是 BPtracer.py）
MAIN_SCRIPT = os.path.join(MAIN_SCRIPT_DIR, "BPtracer.py")  # 主程序路径
# 当前 config 文件路径
CONFIG_SCRIPT = os.path.abspath(__file__) # 默认config路径
# bin路径
BIN_PATH = os.path.join(MAIN_SCRIPT_DIR, 'bin')
# db (database) 路径
DATABASE_PATH = os.path.join(MAIN_SCRIPT_DIR, 'db')

# ====================== 输出路径相关 ======================
# 默认输出路径：当前工作目录
OUTPUT_PATH = os.getcwd()

# 初始化时给一个合理的默认值，避免未定义
SHELL_PATH = os.path.join(OUTPUT_PATH, "shell/")
SARG_OUTPUT_PATH = os.path.join(OUTPUT_PATH, "SARG/")
Kraken2_OUTPUT_PATH = os.path.join(OUTPUT_PATH, "Kraken2/")
HGT_OUTPUT_PATH = os.path.join(OUTPUT_PATH, "WAAFLE/")
SPAdes_OUTPUT_PATH = os.path.join(OUTPUT_PATH, "Assamble_SPADde")
Megahit_OUTPUT_PATH = os.path.join(OUTPUT_PATH, "Assamble_Megahit")
BP_OUTPUT_PATH = os.path.join(OUTPUT_PATH, "BPTracer")

def set_output_path(pwd=None):
    """
    设置分析输出的根目录，并同步更新各模块输出子目录。
    Parameters
    ----------
    pwd : str or None
        用户指定的输出目录。如果为 None，则使用当前工作目录。
    """
    global OUTPUT_PATH, SHELL_PATH, SARG_OUTPUT_PATH, Kraken2_OUTPUT_PATH, HGT_OUTPUT_PATH  # 声明全局变量
    global SPAdes_OUTPUT_PATH, Megahit_OUTPUT_PATH, BP_OUTPUT_PATH, BP_TAX_PATH
    if pwd is not None:
        OUTPUT_PATH = os.path.abspath(pwd)  # Use absolute path
    else:
        OUTPUT_PATH = os.getcwd()  # Default to current working directory
    SHELL_PATH = os.path.join(OUTPUT_PATH, "shell/")
    SARG_OUTPUT_PATH = os.path.join(OUTPUT_PATH, "SARG/")
    Kraken2_OUTPUT_PATH = os.path.join(OUTPUT_PATH, "Kraken2/")
    HGT_OUTPUT_PATH = os.path.join(OUTPUT_PATH, "WAAFLE/")
    SPAdes_OUTPUT_PATH = os.path.join(OUTPUT_PATH, "Assamble_SPADde")
    Megahit_OUTPUT_PATH = os.path.join(OUTPUT_PATH, "Assamble_Megahit")
    BP_OUTPUT_PATH = os.path.join(OUTPUT_PATH, "BPTracer")


#"""Mapping software and Functional gene databases"""
#SARG_MAPPING_SOFTWARE = "diamond blastp"
#SARG_DATABASE = os.path.join(os.path.dirname(__file__), 'db/SARG.3.2.fasta')
#SARG_EVALUE = 1e-5
#SARG_MAX_TARGET_SEQS = 10
#SARG_THREADS = 8
#SARG_FORMAT = 6


# ====================== FastqStat ======================
FASTQSTAT_SOFTWARE =  os.path.join(BIN_PATH, 'FastqStat')


# ====================== Kraken2 相关 ======================
# 默认 kraken2 软件路径和线程数
Kraken2_MAPPING_SOFTWARE = os.path.join(BIN_PATH, "Kraken2")
Kraken2_THREADS = 50  # 默认线程数
# 默认 kraken2 数据库及物种列表
Kraken2_DATABASE = os.path.join(DATABASE_PATH, "Kraken2", "krakenDB-202212")
Kraken2_TAXLIST = os.path.join(Kraken2_DATABASE, "tax.list")


Kraken2_MAPPING_SOFTWARE = os.path.join(BIN_PATH, 'Kraken2')
def set_kraken2_database(database=None):
    """
    设置 Kraken2 使用的数据库。

    Parameters
    ----------
    database : str or None
        - None：使用默认数据库 'krakenDB-202212'
        - 非 None：视为 Kraken2 子目录名，例如 'BPTax_V2'，则数据库路径为
          db/Kraken2/BPTax_V2
    """
    global Kraken2_DATABASE, Kraken2_TAXLIST
    if database is None:
        Kraken2_DATABASE = os.path.join(DATABASE_PATH, 'Kraken2','krakenDB-202212')
        Kraken2_TAXLIST = os.path.join(Kraken2_DATABASE, 'tax.list')
    else:
        Kraken2_DATABASE = os.path.join(DATABASE_PATH, "Kraken2", database)
        Kraken2_TAXLIST = os.path.join(Kraken2_DATABASE, 'tax.list')



# ====================== SPAdes 相关 ======================
SPAdes_MAPPING_SOFTWARE = os.path.join(BIN_PATH, 'SPAdes-3.15.3')
SPAdes_THREADS = 140
SPAdes_MEMORY = 400

# ====================== BP-Tracer 主流程软件 ======================
BP_SAMTOOLS_SOFTWARE = os.path.join(BIN_PATH,"BPTracer/samtools")
BP_DIAMOND_SOFTWARE = os.path.join(BIN_PATH,"BPTracer/diamond blastx")
BP_BLAST_SOFTWARE = os.path.join(BIN_PATH,"BPTracer/blastx")

BP_FQ2FA_SOFTWARE = os.path.join(BIN_PATH,"BPTracer/Fq2fa.pl")
BP_FQ2FA_SOFTWARE2 = "seqtk" # 提供第二种方案1
BP_MINIMAP2 = os.path.join(BIN_PATH,"BPTracer/minimap2")

BP_EXTREA_SOFTWARE = os.path.join(BIN_PATH,"BPTracer/extract_usearch_reads.pl")
# BP_MERGEFA_SOFTWARE = os.path.join(BIN_PATH,"BPTracer/merge_extracted_fa_update_metadate.v2.3.pl")
BP_MERGEFA_SOFTWARE = os.path.join(BIN_PATH,"BPTracer/MergeFa.py")
BP_16S_DATABASE = os.path.join(DATABASE_PATH, 'BPTracer/Gene/gg85_yinxiaole.fasta.mmi')
BP_USCMG_DATABASE = os.path.join(DATABASE_PATH, 'BPTracer/Gene/KO30_DIAMOND.dmnd')
BP_USCMG_LIST = os.path.join(DATABASE_PATH, 'BPTracer/Gene/all_KO30_name.list')

"""BP-Tracer Old USCMG databases"""
BP_USCMG_SOFTWARE = os.path.join(BIN_PATH,"BPTracer/diamond0.8.16 blastx")
BP_USCMG_DATABASE = os.path.join(DATABASE_PATH, 'BPTracer/Gene/KO30_DIAMOND.0.8.16.dmnd')


# ====================== BP-Tracer 功能基因数据库 ======================

BP_EXTRACTEDFA_WINDOW = 200000
BP_META_LIBRARY_SIZE = 300
BP_TAX_DATABASE = os.path.join(DATABASE_PATH, 'BPTracer/Gene/species.info.txt')

# DIAMOND 数据库
BP_ARG_DATABASE = os.path.join(DATABASE_PATH, 'BPTracer/Gene/Gene-ARG.dmnd')
BP_MGE_DATABASE = os.path.join(DATABASE_PATH, 'BPTracer/Gene/Gene-MGE.dmnd')
BP_MRG_DATABASE = os.path.join(DATABASE_PATH, 'BPTracer/Gene/Gene-MRG.dmnd')
BP_VFs_DATABASE = os.path.join(DATABASE_PATH, 'BPTracer/Gene/Gene-VFs.dmnd')
BP_SGs_DATABASE = os.path.join(DATABASE_PATH, 'BPTracer/Gene/Gene-SGs.dmnd')
# 功能基因结构信息
BP_ARG_STRUCTURE = os.path.join(DATABASE_PATH, 'BPTracer/Gene/Gene-ARG.list')
BP_MGE_STRUCTURE = os.path.join(DATABASE_PATH, 'BPTracer/Gene/Gene-MGE.list')
BP_MRG_STRUCTURE = os.path.join(DATABASE_PATH, 'BPTracer/Gene/Gene-MRG.list')
BP_VFs_STRUCTURE = os.path.join(DATABASE_PATH, 'BPTracer/Gene/Gene-VFs.list')
BP_SGs_STRUCTURE = os.path.join(DATABASE_PATH, 'BPTracer/Gene/Gene-SGs.list')
# BLAST 使用的氨基酸序列库
BP_BLASTARG_DATABASE = os.path.join(DATABASE_PATH, 'BPTracer/Gene/Gene-ARG.faa')
BP_BLASTMGE_DATABASE = os.path.join(DATABASE_PATH, 'BPTracer/Gene/Gene-MGE.faa')
BP_BLASTMRG_DATABASE = os.path.join(DATABASE_PATH, 'BPTracer/Gene/Gene-MRG.faa')
BP_BLASTVFs_DATABASE = os.path.join(DATABASE_PATH, 'BPTracer/Gene/Gene-VFs.faa')
BP_BLASTSGs_DATABASE = os.path.join(DATABASE_PATH, 'BPTracer/Gene/Gene-SGs.faa')

# Profile 阈值
BP_LENGTH_THRESHOLD = 25  
BP_IDENTITY_THRESHOLD = 80  
BP_EVALUE_THRESHOLD = 1E-7

# ====================== HGT (WAAFLE) 相关 ======================
# 默认 HGT 数据库：RefseqPan2
BP_HGT_DATABASE  = os.path.join(DATABASE_PATH, 'BPTracer/HGT/RefseqPan2/RefseqPan2')
BP_HGT_STRUCTURE = os.path.join(DATABASE_PATH, 'BPTracer/HGT/RefseqPan2/RefseqPan2_taxonomy.tsv')

def set_HGT_database(database=None):
    global BP_HGT_DATABASE, BP_HGT_STRUCTURE
    if database is None:
        BP_HGT_DATABASE  = os.path.join(DATABASE_PATH, 'BPTracer/HGT/RefseqPan2/RefseqPan2')
        BP_HGT_STRUCTURE = os.path.join(DATABASE_PATH, 'BPTracer/HGT/RefseqPan2/RefseqPan2_taxonomy.tsv')
    else:
        BP_HGT_DATABASE  = os.path.join(DATABASE_PATH, 'BPTracer/HGT/',database,database)
        BP_HGT_STRUCTURE = os.path.join(DATABASE_PATH, 'BPTracer/HGT/', database, f"{database}_taxonomy.tsv")


