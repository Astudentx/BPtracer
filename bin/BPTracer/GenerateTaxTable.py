import pandas as pd
import re
import argparse

def parse_taxonomy(taxonomy_str, level):
    """从分号分隔的分类字符串中提取指定层级的名称"""
    level_prefix = f"{level[0].lower()}__"
    for taxon in taxonomy_str.split(';'):
        if taxon.startswith(level_prefix):
            return taxon.split('__', 1)[1].strip()
    return 'Unknown'


def main(input_file, prefix):
    df = pd.read_csv(input_file, sep='\t')
    #sample_cols = [col for col in df.columns if re.match(r'A\d+', col)]
    sample_cols = df.columns[7:].tolist()  #  修改点：从第8列开始获取样本列（索引7开始）
    
    # 生成各分类层级的汇总文件
    taxonomic_levels = ['Kingdom', 'Phylum', 'Class', 'Order', 'Family', 'Genus', 'Species']
    
    for level in taxonomic_levels:
        # 提取当前层级的分类名称
        df[level] = df['Taxonomy'].apply(lambda x: parse_taxonomy(x, level))
        
        # 按分类名称聚合求和
        agg_df = df.groupby(level, as_index=False)[sample_cols].sum()
        
        # 保存文件
        output_file = f"{prefix}.{level}.ppm.txt"
        agg_df.to_csv(output_file, sep='\t', index=False)
        print(f"Generated {output_file}")

    # 生成Lineage汇总文件
    lineage_df = df.groupby(['TaxID', 'Taxonomy', 'Lineage'], as_index=False)[sample_cols].sum()
    lineage_df = lineage_df[['TaxID'] + sample_cols + ['Taxonomy', 'Lineage']]
    lineage_output_file = f"{prefix}.Lineage.ppm.txt"
    lineage_df.to_csv(lineage_output_file, sep='\t', index=False)
    print(f"Generated {lineage_output_file}")

if __name__ == '__main__':
    # 设置命令行参数解析
    parser = argparse.ArgumentParser(description="Generate taxonomic summary tables from ARGs data.")
    parser.add_argument('-i', '--input', required=True, help="Input file path (e.g., temp.txt)")
    parser.add_argument('-p', '--prefix', required=True, help="Output file prefix (e.g., Tax.ARGs)")
    args = parser.parse_args()

    # 调用主函数
    main(args.input, args.prefix)