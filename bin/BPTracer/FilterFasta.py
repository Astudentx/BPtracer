import pandas as pd
from Bio import SeqIO
import os

def filter_blast_m8(m8_file, output_m8, length_threshold, identity_threshold, evalue_threshold):
    """
    筛选 BLAST6 格式的 m8 文件。

    参数：
    - m8_file (str): 输入的 m8 文件路径。
    - output_m8 (str): 输出的过滤后的 m8 文件路径。
    - length_threshold (int): 最小比对长度。
    - identity_threshold (float): 最小比对相似度。
    - evalue_threshold (float): 最大 E 值阈值。

    返回：
    - filtered_genes (set): 通过筛选的基因 ID 集合。
    """
    # 读取 m8 文件
    blast_df = pd.read_csv(m8_file, sep="\t", header=None, names=[
        "query", "gene", "identity", "alignment_length", "mismatches",
        "gap_opens", "q_start", "q_end", "s_start", "s_end", "evalue", "bit_score"
    ])

    # 筛选数据
    filtered_df = blast_df[
        (blast_df["alignment_length"] >= length_threshold) &
        (blast_df["identity"] >= identity_threshold) &
        (blast_df["evalue"] <= evalue_threshold)
    ]

    # 保存过滤后的 m8 文件
    filtered_df.to_csv(output_m8, sep="\t", index=False, header=False)
    print(f"Filtered m8 file saved to: {output_m8}")

    # 返回通过筛选的基因 ID
    filtered_genes = set(filtered_df["query"])
    return filtered_genes

def filter_fasta_by_genes(fasta_file, output_fasta, filtered_genes):
    """
    根据筛选的基因 ID 过滤 fasta 文件。

    参数：
    - fasta_file (str): 输入的 fasta 文件路径。
    - output_fasta (str): 输出的过滤后的 fasta 文件路径。
    - filtered_genes (set): 通过筛选的基因 ID 集合。
    """
    filtered_genes = set(filtered_genes)  # 确保使用高效的集合操作
    print(f"Number of filtered genes: {len(filtered_genes)}")  # 调试信息
    # 提前加载所有记录以减少磁盘访问
    with open(output_fasta, "w") as out_fasta:
        count = SeqIO.write(
            (record for record in SeqIO.parse(fasta_file, "fasta") if record.id in filtered_genes),
            out_fasta,
            "fasta"
        )
    print(f"Filtered fasta file saved to: {output_fasta} with {count} records.")


def main(m8_file, fasta_file, output_m8, output_fasta, length_threshold=25, identity_threshold=80, evalue_threshold=1e-7):
    """
    主函数，筛选 m8 和 fasta 文件。

    参数：
    - m8_file (str): 输入的 m8 文件路径。
    - fasta_file (str): 输入的 fasta 文件路径。
    - output_m8 (str): 输出的过滤后的 m8 文件路径。
    - output_fasta (str): 输出的过滤后的 fasta 文件路径。
    - length_threshold (int): 最小比对长度，默认 25。
    - identity_threshold (float): 最小比对相似度，默认 80。
    - evalue_threshold (float): 最大 E 值阈值，默认 1e-7。
    """
    # 筛选 m8 文件
    filtered_genes = filter_blast_m8(m8_file, output_m8, length_threshold, identity_threshold, evalue_threshold)

    # 筛选 fasta 文件
    filter_fasta_by_genes(fasta_file, output_fasta, filtered_genes)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Filter m8 and fasta files based on specified criteria")
    parser.add_argument("-m8", required=True, help="Input BLAST6 m8 file")
    parser.add_argument("-fa", required=True, help="Input fasta file")
    parser.add_argument("-o_m8", required=True, help="Output filtered m8 file")
    parser.add_argument("-o_fa", required=True, help="Output filtered fasta file")
    parser.add_argument("-l", type=int, default=25, help="Minimum alignment length (default: 25)")
    parser.add_argument("-id", type=float, default=80, help="Minimum identity (default: 80)")
    parser.add_argument("-e", type=float, default=1e-7, help="E-value threshold (default: 1e-7)")

    args = parser.parse_args()

    main(
        m8_file=args.m8,
        fasta_file=args.fa,
        output_m8=args.o_m8,
        output_fasta=args.o_fa,
        length_threshold=args.l,
        identity_threshold=args.id,
        evalue_threshold=args.e
    )
