import os
import sys

"""Default values for filenames and common constants."""
# 获取主脚本所在目录路径
MAIN_SCRIPT_DIR = os.path.dirname(os.path.abspath(sys.argv[0]))
# 拼接子目录路径
BIN_PATH = os.path.join(MAIN_SCRIPT_DIR, 'bin')
DATABASE_PATH = os.path.join(MAIN_SCRIPT_DIR, 'db')

# 输出路径可能会收到
OUTPUT_PATH = os.getcwd()  # 默认初始化为当前工作目录，防止OUTPUT_PATH无法识别的问题
SHELL_PATH = os.path.join(OUTPUT_PATH, "shell/")  # 初始化路径

def set_output_path(pwd=None):
    global OUTPUT_PATH, SHELL_PATH, SARG_OUTPUT_PATH, Kraken2_OUTPUT_PATH  # 声明全局变量
    global SPAdes_OUTPUT_PATH, megahit_OUTPUT_PATH
    if pwd is not None:
        OUTPUT_PATH = os.path.abspath(pwd)  # Use absolute path
    else:
        OUTPUT_PATH = os.getcwd()  # Default to current working directory
    SHELL_PATH = os.path.join(OUTPUT_PATH, "shell/")
    SARG_OUTPUT_PATH = os.path.join(OUTPUT_PATH, "SARG/")
    Kraken2_OUTPUT_PATH = os.path.join(OUTPUT_PATH, "Kraken2/")
    megahit_OUTPUT_PATH = os.path.join(OUTPUT_PATH, "Assamble_megahit")
    SPAdes_OUTPUT_PATH = os.path.join(OUTPUT_PATH, "Assamble_SPADde")


"""Mapping software and Functional gene databases"""
SARG_MAPPING_SOFTWARE = "diamond blastp"
SARG_DATABASE = os.path.join(DATABASE_PATH, 'db/SARG.3.2.fasta')
SARG_EVALUE = 1e-5
SARG_MAX_TARGET_SEQS = 10
SARG_THREADS = 8
SARG_FORMAT = 6

"""Kraken2 software and k-mer gene databases"""
Kraken2_MAPPING_SOFTWARE = os.path.join(BIN_PATH, 'Kraken2')
Kraken2_DATABASE = os.path.join(DATABASE_PATH, 'Kraken2/kraken2DB')
Kraken2_THREADS = 10
"""SPAdes software"""
SPAdes_MAPPING_SOFTWARE = os.path.join(BIN_PATH, 'SPAdes-3.15.3')
SPAdes_THREADS = 140
SPAdes_MEMORY = 400