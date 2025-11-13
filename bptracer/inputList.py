import pandas as pd
import os

"""
目的是将输入的raw.fq.list定义到一个Class里面
FqData.id
FqData.fq1
FqData.fq2
FqData.num
"""

class DataPaired:
    def __init__(self, sample_id, file1, file2, number):
        self.id = sample_id
        self.file1 = file1
        self.file2 = file2
        self.number = number

def read_paired_list(file):
    # 转换为绝对路径
    abs_raw = os.path.realpath(file)
    all_list = pd.read_csv(abs_raw, sep="\t", header=None)
    id_list = all_list[0]
    file1_list = all_list[1]
    file2_list = all_list[2]
    id_num = id_list.shape[0]
    # 创建 FqData 实例并返回
    data = DataPaired(id_list, file1_list, file2_list, id_num)
    return data

class DataSingle:
    def __init__(self, sample_id, file1, number):
        self.id = sample_id
        self.file1 = file1
        self.number = number

def read_single_list(file):
    # 转换为绝对路径
    abs_raw = os.path.realpath(file)
    all_list = pd.read_csv(abs_raw, sep="\t", header=None)
    id_list = all_list[0]
    file1_list = all_list[1]
    id_num = id_list.shape[0]
    # 创建 FqData 实例并返回
    data = DataSingle(id_list, file1_list, id_num)
    return data

def generate_inputlist(file, output_file, base_path):
    """
    根据输入文件生成路径信息并保存到输出文件。

    Args:
        input_file (str): 输入文件路径。
        output_file (str): 输出文件路径。
        base_path (str): 基础路径。
    """
    # 获取输入文件的绝对路径
    
    abs_raw = os.path.realpath(file)
    all_list = pd.read_csv(abs_raw, sep="\t", header=None)
    id_list = all_list[0]

    output_data = []
    for sample_id in id_list:
        output_line = [
            sample_id,
            f"{base_path}/00.DataStat/{sample_id}/{sample_id}_1.fa",
            f"{base_path}/00.DataStat/{sample_id}/{sample_id}_2.fa",
            f"{base_path}/00.DataStat/{sample_id}/{sample_id}.uscmg.blastx.txt",
            f"{base_path}/00.DataStat/{sample_id}/{sample_id}.sam",
            f"{base_path}/00.DataStat/{sample_id}/meta_data_online.txt"
        ]
        output_data.append(output_line)
        # 转换为 DataFrame 并写入输出文件
        output_df = pd.DataFrame(output_data, columns=["ID", "File1", "File2", "Blastx", "Sam", "MetaData"])
        final_path = os.path.join(base_path,output_file)
        output_df.to_csv(final_path, sep="\t", index=False, header=False)
    print(f"Inputlist set to: {final_path}")