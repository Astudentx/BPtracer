import sys

def main():
    if len(sys.argv) != 4:
        print(f"Usage: python {sys.argv[0]} species.txt ppm.gene.txt1 ppm.gene.txt2")
        sys.exit(1)

    species_file = sys.argv[1]
    gene_file = sys.argv[2]
    output_file = sys.argv[3]

    # 读取物种信息（五列）
    species = {}
    with open(species_file, 'r') as f:
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) >= 5:
                gene_id = parts[0]
                species_name = parts[1]
                tax_id = parts[2]
                taxonomy = parts[3]  # 分类层级
                lineage = parts[4]   # 谱系编号
                species[gene_id] = (species_name, tax_id, taxonomy, lineage)

    # 处理基因列表
    with open(gene_file, 'r') as fin, open(output_file, 'w') as fout:
        header = fin.readline().strip()
        columns = header.split('\t')
        # 新表头添加三列
        fout.write("Gene\tSubtype\tType\tSpecies\tTaxID\tTaxonomy\tLineage\t" + "\t".join(columns[3:]) + "\n")

        for line in fin:
            parts = line.strip().split('\t')
            if len(parts) >= 4:
                gene_id = parts[0]
                # 获取四元组信息，默认四个Unknown
                species_info = species.get(gene_id, ("Unknown", "Unknown", "Unknown", "Unknown"))
                species_name, tax_id, taxonomy, lineage = species_info
                # 写入三列新增数据
                fout.write(
                    f"{parts[0]}\t{parts[1]}\t{parts[2]}\t{species_name}\t"
                    f"{tax_id}\t{taxonomy}\t{lineage}\t" + 
                    "\t".join(parts[3:]) + "\n"
                )

if __name__ == "__main__":
    main()