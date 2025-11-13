import sys
from collections import defaultdict

def load_taxonomy(species_file, tax_table):
    """加载分类信息"""
    species = defaultdict(lambda: [0.0]*tax_columns)
    
    # 先读取表头获取列数
    with open(tax_table) as f:
        headers = f.readline().strip().split('\t')
        tax_columns = len(headers) - 1  # 第一列为物种名
    
    # 初始化物种字典
    with open(species_file) as f:
        for line in f:
            species[line.strip()] = [0.0]*tax_columns
    
    # 填充实际数据
    with open(tax_table) as f:
        f.readline()  # 跳过表头
        for line in f:
            parts = line.strip().split('\t')
            sp = parts[0].replace(' ', '-')
            if sp in species:
                try:
                    species[sp] = [float(x) for x in parts[1:1+tax_columns]]
                except ValueError:
                    pass
    return species, tax_columns

def process_genes(gene_list_file):
    """处理基因-物种映射"""
    gene_map = defaultdict(set)
    with open(gene_list_file) as f:
        for line in f:
            parts = line.strip().split('\t')
            for gene in parts[1:]:  # 第一列为GeneID
                prefix = gene.split('_', 1)[0]
                gene_map[parts[0]].add(prefix)
    return gene_map

def main():
    if len(sys.argv) != 6:
        print(f"Usage: {sys.argv[0]} species.txt gene.list taxonomy.table.S input.txt output.txt")
        sys.exit(1)

    # 参数解析
    species_file, gene_list, tax_table, input_file, output_file = sys.argv[1:6]
    
    # 加载数据
    species_data, tax_columns = load_taxonomy(species_file, tax_table)
    gene_data = process_genes(gene_list)
    
    # 处理输入文件
    with open(input_file) as fin, open(output_file, 'w') as fout:
        # 处理表头
        headers = fin.readline().strip().split('\t')
        new_header = headers[:3] + ["Species"] + headers[3:]
        fout.write("\t".join(new_header) + "\n")
        
        # 处理数据行
        for line in fin:
            parts = line.strip().split('\t')
            if len(parts) < 4: continue
            
            gene_id, subtype, gtype = parts[:3]
            values = list(map(float, parts[3:]))
            
            # 获取关联物种
            related_species = gene_data.get(gene_id, set())
            if not related_species:
                continue
            
            # 计算总权重
            total_weights = [
                sum(species_data[sp][i] for sp in related_species)
                for i in range(tax_columns)
            ]
            
            # 生成校正后数据
            for sp in related_species:
                sp_weights = species_data[sp]
                adjusted = []
                for i, val in enumerate(values):
                    if total_weights[i] > 0:
                        adj_val = val * sp_weights[i] / total_weights[i]
                    else:
                        adj_val = val / len(related_species)
                    adjusted.append(f"{adj_val:.8f}")
                
                output_line = "\t".join([
                    gene_id, subtype, gtype, sp
                ] + adjusted)
                fout.write(output_line + "\n")

if __name__ == "__main__":
    main()