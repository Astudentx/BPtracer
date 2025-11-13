import os
import argparse
from itertools import product

def main():
    parser = argparse.ArgumentParser(description="参数化脚本生成器")
    
    # 必需参数
    parser.add_argument("--pwd", required=True, help="输出根目录路径")
    parser.add_argument("--input_file", required=True, help="输入blast结果文件")
    parser.add_argument("--meta_file", required=True, help="元数据文件路径")
    parser.add_argument("--db_path", required=True, help="基因数据库路径")
    parser.add_argument("--gene_list", required=True, help="基因列表路径")
    
    # 可选参数
    parser.add_argument("--id_values", default="70,75,80,85,90,95,100", help="ID阈值列表")
    parser.add_argument("--l_values", default="30,50,80,100", help="长度阈值列表")
    parser.add_argument("--base_output", default="ARGs", help="输出文件前缀")

    args = parser.parse_args()

    # 创建输出目录
    output_root = os.path.abspath(args.pwd)
    shell_dir = os.path.join(output_root, "shell")
    os.makedirs(shell_dir, exist_ok=True)

    # 参数解析
    id_list = list(map(int, args.id_values.split(',')))
    l_list = list(map(int, args.l_values.split(',')))

    for id_val, l_val in product(id_list, l_list):
        output_dir = os.path.join(output_root, f"{args.base_output}_id{id_val}_l{l_val}")
        os.makedirs(output_dir, exist_ok=True)
        
        script_path = os.path.join(shell_dir, f"run_{args.base_output}_id{id_val}_l{l_val}.sh")
        
        with open(script_path, 'w') as f:
            f.write(f"""#!/bin/bash
# 主分析命令
python3 /mnt/sdb/zhangyz/bin/BPtracer/bin/BPTracer/GeneAbundance.py \\
  -i {os.path.abspath(args.input_file)} \\
  -m {os.path.abspath(args.meta_file)} \\
  -p OUT.{args.base_output} \\
  -db {os.path.abspath(args.db_path)} \\
  -s {os.path.abspath(args.gene_list)} \\
  -o {output_dir} \\
  -l {l_val} \\
  -id {id_val} \\
  -e 1e-07

# 原始子表生成命令（保持完全不变）
# ppm
python3 /mnt/sdb/zhangyz/bin/BPtracer/bin/BPTracer/GenerateSubTable.py \\
  --input  {output_dir}/OUT.{args.base_output}.ppm.txt \\
  --output  {output_dir}/OUT.{args.base_output}.ppm.Type.txt \\
  --group_by Type

python3 /mnt/sdb/zhangyz/bin/BPtracer/bin/BPTracer/GenerateSubTable.py \\
  --input  {output_dir}/OUT.{args.base_output}.ppm.txt \\
  --output  {output_dir}/OUT.{args.base_output}.ppm.Subtype.txt \\
  --group_by Subtype

# 16s
python3 /mnt/sdb/zhangyz/bin/BPtracer/bin/BPTracer/GenerateSubTable.py \\
  --input  {output_dir}/OUT.{args.base_output}.16s.txt \\
  --output  {output_dir}/OUT.{args.base_output}.16s.Type.txt \\
  --group_by Type

python3 /mnt/sdb/zhangyz/bin/BPtracer/bin/BPTracer/GenerateSubTable.py \\
  --input  {output_dir}/OUT.{args.base_output}.16s.txt \\
  --output  {output_dir}/OUT.{args.base_output}.16s.Subtype.txt \\
  --group_by Subtype

# cellNumber
python3 /mnt/sdb/zhangyz/bin/BPtracer/bin/BPTracer/GenerateSubTable.py \\
  --input  {output_dir}/OUT.{args.base_output}.cell_number.txt \\
  --output  {output_dir}/OUT.{args.base_output}.cell_number.Type.txt \\
  --group_by Type

python3 /mnt/sdb/zhangyz/bin/BPtracer/bin/BPTracer/GenerateSubTable.py \\
  --input  {output_dir}/OUT.{args.base_output}.cell_number.txt \\
  --output  {output_dir}/OUT.{args.base_output}.cell_number.Subtype.txt \\
  --group_by Subtype

# 后续处理
python3 /mnt/sdb/zhangyz/bin/BPtracer/bin/BPTracer/GeneAddTax.py \\
  /mnt/sdb/zhangyz/bin/BPtracer/db/BPTracer/Gene/species.info.txt \\
  {output_dir}/OUT.{args.base_output}.ppm.txt \\
  {output_dir}/Tax.{args.base_output}.ppm.txt

python3 /mnt/sdb/zhangyz/bin/BPtracer/bin/BPTracer/GenerateTaxTable.py \\
  -i {output_dir}/Tax.{args.base_output}.ppm.txt \\
  -p {output_dir}/Tax.{args.base_output}

echo "任务完成：id={id_val} l={l_val}"
""")
        print(f"生成脚本：{script_path}")

if __name__ == "__main__":
    main()