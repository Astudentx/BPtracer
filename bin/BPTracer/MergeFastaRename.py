import os
import argparse

def merge_fasta(outdir, sample, extracted_fasta):
    # 定义输入文件路径
    extract1 = os.path.join(outdir, f"{sample}.extract_1.fa")
    extract2 = os.path.join(outdir, f"{sample}.extract_2.fa")

    # 如果输出文件已存在，先删除
    if os.path.exists(extracted_fasta):
        os.remove(extracted_fasta)

    # 检查输入文件是否存在
    if not (os.path.exists(extract1) and os.path.exists(extract2)):
        raise RuntimeError(f"Missing files: {extract1 if not os.path.exists(extract1) else extract2}")

    # 合并文件内容
    count = 1
    with open(extracted_fasta, 'w') as out_fasta:
        for file_path in [extract1, extract2]:
            with open(file_path, 'r') as f:
                for header in f:
                    sequence = next(f).strip()
                    out_fasta.write(f">{sample}_{count}\n{sequence}\n")
                    count += 1

def parse_args():
    parser = argparse.ArgumentParser(description="Merge FASTA files.")
    parser.add_argument("--outdir", help="Output directory for results.")
    parser.add_argument("--sample_id", help="Sample name.")
    parser.add_argument("--extracted_fasta", help="Output combined FASTA file.")
    return parser.parse_args()

def main():
    args = parse_args()
    merge_fasta(args.outdir, args.sample_id, args.extracted_fasta)

if __name__ == "__main__":
    main()