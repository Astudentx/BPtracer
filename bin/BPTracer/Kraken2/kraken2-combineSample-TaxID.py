import argparse
import os
from collections import defaultdict

def main():
    parser = argparse.ArgumentParser(
        description="合并Kraken2报告文件生成丰度矩阵，支持多层级分类信息和独立Lineage列"
    )
    parser.add_argument(
        "-i", "--input",
        nargs="+",
        required=True,
        help="输入文件列表（Kraken2报告文件）"
    )
    parser.add_argument(
        "-n", "--name",
        nargs="+",
        help="手动指定样本名称（数量必须与输入文件一致）"
    )
    parser.add_argument(
        "-o", "--output",
        required=True,
        help="输出文件名（如：merged_abundance.tsv）"
    )
    parser.add_argument(
        "-f", "--field",
        default="new_est_reads",
        choices=["kraken_assigned_reads", "added_reads", "new_est_reads", "fraction_total_reads"],
        help="选择丰度字段"
    )
    parser.add_argument(
        "--taxonomy",
        help="分类信息文件路径"
    )
    parser.add_argument(
        "-l", "--level",
        choices=["Kingdom", "Phylum", "Class", "Order", "Family", "Genus", "Species"],
        default="Species",
        help="指定优先匹配的分类层级（默认：Species）"
    )
    args = parser.parse_args()

    # 样本名称校验
    if args.name and len(args.name) != len(args.input):
        print(f"错误：样本名称数量（{len(args.name)}）与输入文件数量（{len(args.input)}）不匹配")
        exit(1)

    # 字段索引映射
    header_columns = [
        "name", "taxonomy_id", "taxonomy_lvl",
        "kraken_assigned_reads", "added_reads",
        "new_est_reads", "fraction_total_reads"
    ]
    try:
        field_index = header_columns.index(args.field)
    except ValueError:
        print(f"错误：字段 '{args.field}' 不存在。可选字段：{', '.join(header_columns)}")
        exit(1)

    # 分类信息加载（关键修正：列名适配）
    taxonomy_map = {}
    id_mappings = defaultdict(list)
    level_columns = {
        "Kingdom": {"name_idx": 1, "id_idx": 8},  # 第1列为Kindom（注意原文件拼写错误）
        "Phylum": {"name_idx": 2, "id_idx": 9},
        "Class": {"name_idx": 3, "id_idx": 10},
        "Order": {"name_idx": 4, "id_idx": 11},
        "Family": {"name_idx": 5, "id_idx": 12},
        "Genus": {"name_idx": 6, "id_idx": 13},
        "Species": {"name_idx": 7, "id_idx": 14}
    }
    
    if args.taxonomy:
        with open(args.taxonomy, 'r') as tax_f:
            headers = tax_f.readline().strip().split('\t')
            for line in tax_f:
                parts = line.strip().split('\t')
                tax_id = parts[0]
                
                # 构建各层级映射
                for level in level_columns:
                    col = level_columns[level]
                    level_id = parts[col["id_idx"]]
                    if level_id:  # 确保ID不为空
                        id_mappings[level].append((level_id, tax_id))
                
                # 存储完整分类信息
                taxonomy_map[tax_id] = {
                    "names": [parts[level_columns[level]["name_idx"]] for level in level_columns],
                    "ids": [parts[level_columns[level]["id_idx"]] for level in level_columns]
                }

    # 数据结构初始化
    data = defaultdict(dict)
    samples = []
    seen_samples = set()

    # 处理输入文件
    for idx, file_path in enumerate(args.input):
        sample = args.name[idx] if args.name else os.path.splitext(os.path.basename(file_path))[0]
        if sample in seen_samples:
            print(f"警告：样本 {sample} 重复，跳过文件 {file_path}")
            continue
        seen_samples.add(sample)
        samples.append(sample)

        with open(file_path, 'r') as f:
            next(f)  # 跳过标题行
            for line in f:
                parts = line.strip().split('\t')
                if len(parts) < 7: continue
                tax_id = parts[1]
                try:
                    value = int(parts[field_index]) if args.field != "fraction_total_reads" else float(parts[field_index])
                except:
                    value = 0
                data[tax_id][sample] = value

    # 排序TaxID
    tax_ids = sorted(data.keys(), key=lambda x: int(x))

    # 构建优先级列表
    priority = ["Species", "Genus", "Family", "Order", "Class", "Phylum", "Kingdom"]
    if args.level:
        priority.remove(args.level)
        priority.insert(0, args.level)

    # 写入输出文件
    with open(args.output, 'w') as out_f:
        # 表头
        header = ["ID"] + samples + ["Taxonomy", "Lineage"]
        out_f.write("\t".join(header) + "\n")

        for tax_id in tax_ids:
            row = [tax_id]
            # 样本数据
            row += [str(data[tax_id].get(s, 0)) for s in samples]
            
            # 查找分类信息
            taxonomy = "NA"
            lineage = "NA"
            found = False
            
            # 按优先级查找
            for level in priority:
                for (id_val, mapped_id) in id_mappings.get(level, []):
                    if id_val == tax_id and mapped_id in taxonomy_map:
                        info = taxonomy_map[mapped_id]
                        # 根据层级截断
                        level_idx = list(level_columns.keys()).index(level)
                        taxonomy = ";".join(info["names"][:level_idx+1])
                        lineage = ";".join(info["ids"][:level_idx+1])
                        found = True
                        break
                if found: break
            
            row += [taxonomy, lineage]
            out_f.write("\t".join(row) + "\n")

if __name__ == "__main__":
    main()