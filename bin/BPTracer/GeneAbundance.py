import pandas as pd
import os
import re
import argparse
from collections import defaultdict


def parse_arguments():
    """
    解析命令行参数，用于ARG识别管道的第二阶段。
    参数说明:
    -i: 输入的BLAST6结果文件路径 (必需)。
    -m: 阶段一生成的元数据文件路径 (必需)。
    -db: 功能基因数据库文件路径，faa格式 (必需)。
    -s: 基因分类结构文件路径 (必需)。
    -p: 输出文件前缀 (必需)。
    -l: 最小比对长度，默认为25。
    -e: E值阈值，默认为1e-7。
    -id: 最小序列相似度，默认为80。
    -o: 输出文件路径，默认为当前目录。
    """
    parser = argparse.ArgumentParser(description="ARG Identification Pipeline - Stage 2")
    parser.add_argument("-i", required=True, help="Input BLAST6 result file")
    parser.add_argument("-m", required=True, help="Metadata file from stage one")
    parser.add_argument("-db", required=True, help="Database of functional genes, faa format")
    parser.add_argument("-s", required=True, help="Path to the classification structure file of genes")
    parser.add_argument("-p", required=True, help="Prefix")
    parser.add_argument("-l", type=int, default=25, help="Minimum alignment length (default: 25)")
    parser.add_argument("-e", type=float, default=1e-7, help="E-value threshold (default: 1e-7)")
    parser.add_argument("-id", type=float, default=80, help="Minimum identity (default: 80)")
    parser.add_argument("-o", default="./", help="Output Path")
    return parser.parse_args()

def process_metadata_bak(meta_file):
    """
    处理元数据文件。
    参数:
    - meta_file (str): 元数据文件的路径，包含样本的基本信息。
    返回:
    - sample_info (dict): 样本信息的字典，键为样本名称，值为一个字典，包含reads、16S读数和细胞数量。
    异常:
    - 如果文件格式不符合预期，会抛出RuntimeError。
    """
    ...
    try:
        # 读取 metadata 文件
        df = pd.read_csv(meta_file, sep="\t")
        df.columns = ["SampleID","Name", "LibrarySize","#ofReads","#of16Sreads","CellNumber"]
        # df.columns = ["SampleID","Name", "Category", "LibrarySize","#ofReads","#of16Sreads","CellNumber"]

        # 确保列名无误
        required_columns = ["Name", "#ofReads", "#of16Sreads", "CellNumber"]
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns in metadata: {missing_columns}")

        # 重命名列以便于访问
        df.rename(columns={"#ofReads": "reads", "#of16Sreads": "16s", "CellNumber": "cell_number"}, inplace=True)
        
        # 将样本 ID 作为索引
        sample_info = df.set_index("Name")[["reads", "16s", "cell_number"]].to_dict(orient="index")
    except Exception as e:
        raise RuntimeError(f"Error processing metadata file: {e}")
    
    return sample_info


def process_metadata(meta_file):
    """
    处理元数据文件。
    参数:
    - meta_file (str): 元数据文件的路径，包含样本的基本信息。
    返回:
    - sample_info (dict): 样本信息的字典，键为样本名称，值为一个字典，包含reads、16S读数和细胞数量。
    异常:
    - 如果文件格式不符合预期，会抛出RuntimeError。
    """
    try:
        # 读取 metadata 文件
        df = pd.read_csv(meta_file, sep="\t")
        
        # 定义所需的列
        required_columns = ["SampleID", "Name", "LibrarySize", "#ofReads", "#of16Sreads", "CellNumber"]
        
        # 检查所需的列是否都存在
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns in metadata: {missing_columns}")
        
        # 只保留需要的列
        df = df[required_columns]
        
        # 重命名列以便于访问
        df.rename(columns={"#ofReads": "reads", "#of16Sreads": "16s", "CellNumber": "cell_number"}, inplace=True)
        
        # 将样本名称作为索引并提取所需数据
        sample_info = df.set_index("Name")[["reads", "16s", "cell_number"]].to_dict(orient="index")
    except Exception as e:
        raise RuntimeError(f"Error processing metadata file: {e}")
    
    return sample_info



def parse_ardb_files(ardb_fasta, ardb_structure):
    """
    解析ARDB数据库中的基因序列和分类信息。
    参数:
    - ardb_fasta (str): ARDB基因的FASTA文件路径。
    - ardb_structure (str): ARDB基因分类结构文件路径。
    返回:
    - gene_lengths (dict): 每个基因的长度字典，键为基因ID，值为长度。
    - gene_structure (dict): 包含基因的类型和亚型信息的字典。
    异常:
    - 如果文件读取或解析失败，会抛出RuntimeError。
    """
    gene_lengths = {}
    gene_structure = {"type": {}, "subtype": {}}

    # 处理 FASTA 文件以获取基因长度
    try:
        with open(ardb_fasta, "r") as f:
            for line in f:
                if line.startswith(">"):
                    gene_id = line.split()[0][1:]
                    seq = next(f).strip()
                    gene_lengths[gene_id] = len(seq)
    except Exception as e:
        raise RuntimeError(f"Error processing ARDB FASTA file: {e}")

    # 处理结构文件以获取基因分类信息
    try:
        ardb_df = pd.read_csv(ardb_structure, sep="\t")
        for _, row in ardb_df.iterrows():
            category = row["Categories_in_database"]
            gene_ids_str = row["Corresponding_ids"]
            
            # 解析 `Corresponding_ids` 列
            gene_ids = gene_ids_str.strip("[]").replace("'", "").split(", ")
            
            # 分类信息
            for gene_id in gene_ids:
                gene_structure["type"][gene_id] = category.split("__")[0]  # 大类
                gene_structure["subtype"][gene_id] = category               # 亚型
    except Exception as e:
        raise RuntimeError(f"Error processing ARDB structure file: {e}")

    return gene_lengths, gene_structure


def parse_blast6(blast_file, gene_lengths, length_threshold, identity_threshold, evalue_threshold, folder):
    """
    解析BLAST6格式的输出文件并过滤结果。
    参数:
    - blast_file (str): BLAST6结果文件路径。
    - gene_lengths (dict): 基因长度信息字典。
    - length_threshold (int): 最小比对长度。
    - identity_threshold (float): 最小比对相似度。
    - evalue_threshold (float): E值阈值。
    返回:
    - sample_hits_rate (DataFrame): 样本中基因的比对比例表。
    - sample_hits_count (DataFrame): 样本中基因的比对次数表。
    异常:
    - 如果文件解析或数据过滤失败，会抛出RuntimeError。
    """
    try:
        # 读取 BLAST6 文件
        blast_df = pd.read_csv(blast_file, sep="\t", header=None, names=[
            "query", "gene", "identity", "alignment_length", "mismatches", 
            "gap_opens", "q_start", "q_end", "s_start", "s_end", "evalue", "bit_score"
        ])

        # 过滤数据
        filtered_df = blast_df[
            (blast_df["alignment_length"] >= length_threshold) & 
            (blast_df["identity"] >= identity_threshold) & 
            (blast_df["evalue"] <= evalue_threshold)
        ].copy()

        # 提取核心样本名称
        filtered_df.loc[:, "core_query"] = filtered_df["query"].str.replace(r"_\d+$", "", regex=True)

        # 计算比对比例
        filtered_df["ratio"] = filtered_df.apply(
            lambda row: row["alignment_length"] / gene_lengths.get(row["gene"], 1),
            axis=1
        )

        # 按样本和基因分组，累加比对比例
        ratio_grouped = filtered_df.groupby(["core_query", "gene"])["ratio"].sum().reset_index()

        # 生成比率表
        sample_hits_rate = ratio_grouped.pivot_table(index="core_query", columns="gene", values="ratio", fill_value=0)

        # 按样本和基因分组，统计比对次数
        count_grouped = filtered_df.groupby(["core_query", "gene"]).size().reset_index(name="count")

        # 生成计数表
        sample_hits_count = count_grouped.pivot_table(index="core_query", columns="gene", values="count", fill_value=0)
    except Exception as e:
        raise RuntimeError(f"Error processing BLAST6 file: {e}")
    
    
    # 输出为统计表
    path1 = os.path.join(folder, "sample_hits_rate.txt")
    path2 = os.path.join(folder, "sample_hits_count.txt")
    try:
        # 保存为 tab 分隔的文本文件
        sample_hits_rate.to_csv(path1, sep="\t", index=True)
        print(f"Sample hits rate saved to: {path1}")
        
        sample_hits_count.to_csv(path2, sep="\t", index=True)
        print(f"Sample hits count saved to: {path2}")
    except Exception as e:
        raise RuntimeError(f"Error saving output files: {e}")
    
    return sample_hits_rate, sample_hits_count



def calculate_normalized_values(sample_hits_rate,sample_hits_count, sample_info, gene_structure, gene_lengths):
    """
    根据样本信息和基因比对结果计算标准化的值。
    参数:
    - sample_hits_rate (DataFrame): 样本中基因的比对比例表。
    - sample_hits_count (DataFrame): 样本中基因的比对次数表。
    - sample_info (dict): 样本的基本信息字典。
    - gene_structure (dict): 基因分类结构信息字典。
    - gene_lengths (dict): 基因长度信息字典。
    返回:
    - results (dict): 包含标准化值的嵌套字典，支持PPM、16S和细胞数标准化。
    """

    # 初始化结果存储结构
    results = {
        "ppm": defaultdict(lambda: defaultdict(float)),
        "16s": defaultdict(lambda: defaultdict(float)),
        "cell_number": defaultdict(lambda: defaultdict(float)),
    }

    # 遍历样本
    for sample in sample_hits_rate.index:
        if sample not in sample_info:
            print(f"Warning: Sample {sample} not found in metadata.")
            continue

        # 获取样本信息
        reads = sample_info[sample].get("reads", 0)
        sixteen_s = sample_info[sample].get("16s", 0)
        cell_number = sample_info[sample].get("cell_number", 0)

        if reads <= 0 or sixteen_s <= 0 or cell_number <= 0:
            print(f"Invalid metadata for sample {sample}: reads={reads}, 16s={sixteen_s}, cell_number={cell_number}")
            continue

        # 遍历每个基因
        for gene in sample_hits_rate.columns:
            ratio_sum = sample_hits_rate.at[sample, gene]
            # 16S 正规化
            results["16s"][sample][gene] = ratio_sum / sixteen_s

            # 细胞数正规化
            results["cell_number"][sample][gene] = ratio_sum / cell_number
        
        # 遍历每个基因        
        for gene in sample_hits_rate.columns:
            count = sample_hits_count.at[sample, gene]
            # PPM 正规化
            results["ppm"][sample][gene] = (count * 1e6) / reads
        

    return results




def write_results(output_prefix, results, sample_info, gene_structure, folder):
    """
    将标准化结果写入文件。
    参数:
    - output_prefix (str): 输出文件的前缀。
    - results (dict): 标准化结果字典。
    - sample_info (dict): 样本信息字典。
    - gene_structure (dict): 基因分类结构信息字典。
    异常:
    - 如果文件写入失败，会抛出RuntimeError。
    """
    try:
        # 获取所有样本名称
        sample_names = list(sample_info.keys())

        # 初始化输出表结构
        for result_type in ["ppm", "16s", "cell_number"]:
            rows = []

            # 遍历每个基因并生成输出行
            for gene, subtype in gene_structure["subtype"].items():
                type_ = gene_structure["type"].get(gene, "Unknown")  # 获取类型
                values = [results[result_type].get(sample, {}).get(gene, 0) for sample in sample_names]

                # 添加一行到结果
                rows.append([gene, subtype, type_] + values)

            # 创建 DataFrame
            columns = ["Gene", "Subtype", "Type"] + sample_names
            output_df = pd.DataFrame(rows, columns=columns)

            # 写入文件
            output_file = f"{output_prefix}.{result_type}.txt"
            output_path = os.path.join(folder, output_file)
            output_df.to_csv(output_path, sep="\t", index=False)
            print(f"{result_type.capitalize()} results written to {output_file}")
    except Exception as e:
        raise RuntimeError(f"Error writing results: {e}")



def main():
    args = parse_arguments()
    sample_info = process_metadata(args.m)
    gene_lengths, gene_structure = parse_ardb_files(args.db, args.s)
    sample_hits_rate, sample_hits_count = parse_blast6(args.i, gene_lengths, args.l, args.id, args.e, args.o)
    results = calculate_normalized_values(sample_hits_rate,sample_hits_count, sample_info, gene_structure, gene_lengths)  # 修复参数
    write_results(args.p, results, sample_info, gene_structure, args.o)

if __name__ == "__main__":
    main()

# 脚本调试
#sample_info = process_metadata("/mnt/sdb/zhangyz/bin/BPtracer/tests/BPTracer_GeneAbundance/meta_data_online.txt")
#ardb_fasta = "/mnt/sdb/zhangyz/bin/TAVMM/DB/ARG-uniq.fa"
#ardb_structure = "/mnt/sdb/zhangyz/bin/TAVMM/DB/ARG-uniq.structure"
#gene_lengths, gene_structure = parse_ardb_files(ardb_fasta, ardb_structure)
#sample_hits_rate, sample_hits_count  = parse_blast6("/mnt/sdb/zhangyz/bin/BPtracer/tests/BPTracer_GeneAbundance/blastx.out", gene_lengths, 25, 80,  1e-7)
#results = calculate_normalized_values(sample_hits_rate, sample_hits_count,sample_info,  gene_structure, gene_lengths)
#results
#write_results(args.o, results, sample_info, gene_structure)

#python3  ../../../bin/BPTracer/GeneAbundance.py -m meta_data_online.txt  -p ARG -i blastx.out -d /mnt/sdb/zhangyz/bin/TAVMM/DB/ARG-uniq.fa -s /mnt/sdb/zhangyz/bin/TAVMM/DB/ARG-uniq.structure -o  /mnt/sdb/zhangyz/bin/BPtracer/tests/BPTracer_GeneAbundance/ARGs
#python3  ../../../bin/BPTracer/GeneAbundance.py -i extracted.fa -m final.meta_data_online.txt  -p ARG -i blastx.out -db /mnt/sdb/zhangyz/bin/TAVMM/DB/ARG-uniq.fa -s /mnt/sdb/zhangyz/bin/TAVMM/DB/ARG-uniq.structure -o  /mnt/sdb/zhangyz/bin/BPtracer/tests/BPTracer_GeneAbundance/ARGs
