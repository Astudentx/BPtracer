import textwrap
from bptracer.BaseRunner import BaseRunner
import os
from bptracer import config

class FastqStatRunner(BaseRunner):
    def build_command(self):
        config = self.params.get('config')
        fqName = self.params.get('fqlist')   
        fqlist = os.path.realpath(fqName)
        statpath = os.path.join(config.OUTPUT_PATH,"FastqStat")
        cmd = textwrap.dedent(rf"""
        mkdir -p {statpath}
        cd {statpath}
        java -jar  {config.FASTQ_STAT_SOFTWARE}/FastqStat.jar -i {fqlist}   > stat.main.xls
        python {config.FASTQ_COMBINE_SOFTWARE}
        """)
        return cmd
                              

class Kraken2Runner(BaseRunner):
    def build_command(self):
        # 设置接口参数
        config = self.params.get('config')
        id = self.params.get('id')
        file1 = self.params.get('file1')
        file2 = self.params.get('file2')


        cmd = textwrap.dedent(rf"""
        cd {config.Kraken2_OUTPUT_PATH}
        {config.Kraken2_MAPPING_SOFTWARE} --db {config.Kraken2_DATABASE} --threads {config.Kraken2_THREADS} --quick --report-zero-counts --gzip-compressed --paired --output {id}.readinfo --report {id}.report {file1} {file2}
        {config.KrakenTools_REPORT2MPA_SOFTWARE} -r {id}.report -o {id}.mpa
        {config.Bracken_ESTABUNDANCE_SOFTWARE} -t 1 -k {config.Kraken2_DATABASE}/database150mers.kmer_distrib -i {id}.report -o {id}.report.D -l D
        {config.Bracken_ESTABUNDANCE_SOFTWARE} -t 1 -k {config.Kraken2_DATABASE}/database150mers.kmer_distrib -i {id}.report -o {id}.report.P -l P
        {config.Bracken_ESTABUNDANCE_SOFTWARE} -t 1 -k {config.Kraken2_DATABASE}/database150mers.kmer_distrib -i {id}.report -o {id}.report.C -l C
        {config.Bracken_ESTABUNDANCE_SOFTWARE} -t 1 -k {config.Kraken2_DATABASE}/database150mers.kmer_distrib -i {id}.report -o {id}.report.O -l O
        {config.Bracken_ESTABUNDANCE_SOFTWARE} -t 1 -k {config.Kraken2_DATABASE}/database150mers.kmer_distrib -i {id}.report -o {id}.report.F -l F
        {config.Bracken_ESTABUNDANCE_SOFTWARE} -t 1 -k {config.Kraken2_DATABASE}/database150mers.kmer_distrib -i {id}.report -o {id}.report.G -l G
        {config.Bracken_ESTABUNDANCE_SOFTWARE} -t 1 -k {config.Kraken2_DATABASE}/database150mers.kmer_distrib -i {id}.report -o {id}.report.S -l S
        # rm {id}.readinfo {id}.report
        """)
        return cmd
    
    
class Kraken2Runner2(BaseRunner):
    def build_command(self):
        # 设置接口参数
        config = self.params.get('config')
        id_list = self.params.get('id_list')
        lineage = self.params.get('lineage')

        
        id_list_D =  " ".join([s + ".report.D" for s in id_list])
        id_list_P =  " ".join([s + ".report.P" for s in id_list])
        id_list_C =  " ".join([s + ".report.C" for s in id_list])
        id_list_O =  " ".join([s + ".report.O" for s in id_list])
        id_list_F =  " ".join([s + ".report.F" for s in id_list])
        id_list_G =  " ".join([s + ".report.G" for s in id_list])
        id_list_S =  " ".join([s + ".report.S" for s in id_list])
        id_list2 = ",".join(id_list)
        id_list3 = " ".join(id_list)
        trim_path = os.path.join(config.OUTPUT_PATH, "FastqStat")
        
        cmd = textwrap.dedent(rf"""
        cd {config.Kraken2_OUTPUT_PATH}
        {config.Bracken_COMBINE_SOFTWARE} --files {id_list_D} --names {id_list2} -o taxonomy.D
        {config.Bracken_COMBINE_SOFTWARE} --files {id_list_P} --names {id_list2} -o taxonomy.P
        {config.Bracken_COMBINE_SOFTWARE} --files {id_list_C} --names {id_list2} -o taxonomy.C
        {config.Bracken_COMBINE_SOFTWARE} --files {id_list_O} --names {id_list2} -o taxonomy.O
        {config.Bracken_COMBINE_SOFTWARE} --files {id_list_F} --names {id_list2} -o taxonomy.F
        {config.Bracken_COMBINE_SOFTWARE} --files {id_list_G} --names {id_list2} -o taxonomy.G
        {config.Bracken_COMBINE_SOFTWARE} --files {id_list_S} --names {id_list2} -o taxonomy.S

        # 界门纲目科属种复杂分析版本,需要stat.main.xls 这个不适用于大多数的版本
        # perl  {config.BIN_PATH}/BPTracer/Kraken2/kraken2-mergeStat-unclassfied-New.pl -prefix taxonomy -trim {trim_path}/stat.main.xls -tax {config.Kraken2_TAXLIST}  -out Final
        
        # 界门纲目科属种简单版本
        perl  {config.BIN_PATH}/BPTracer/Kraken2/kraken2-mergeStat-New.pl -prefix taxonomy -tax {config.Kraken2_TAXLIST}  -out TaxAbu
        """)
        
        if lineage != "F":
            cmd += textwrap.dedent(rf"""
        # TaxID合并版本分析
        {config.BIN_PATH}/BPTracer/Kraken2/kraken2-combineSample-TaxID.py -i {id_list_D}  -l Kingdom  -n {id_list3} --taxonomy {config.Kraken2_DATABASE}/Kraken2.Taxonomy.refseq_240720.txt -o TaxIDAbu.D
        {config.BIN_PATH}/BPTracer/Kraken2/kraken2-combineSample-TaxID.py -i {id_list_P}  -l Phylum   -n {id_list3} --taxonomy {config.Kraken2_DATABASE}/Kraken2.Taxonomy.refseq_240720.txt -o TaxIDAbu.P
        {config.BIN_PATH}/BPTracer/Kraken2/kraken2-combineSample-TaxID.py -i {id_list_C}  -l Class    -n {id_list3} --taxonomy {config.Kraken2_DATABASE}/Kraken2.Taxonomy.refseq_240720.txt -o TaxIDAbu.C
        {config.BIN_PATH}/BPTracer/Kraken2/kraken2-combineSample-TaxID.py -i {id_list_O}  -l Order    -n {id_list3} --taxonomy {config.Kraken2_DATABASE}/Kraken2.Taxonomy.refseq_240720.txt -o TaxIDAbu.O
        {config.BIN_PATH}/BPTracer/Kraken2/kraken2-combineSample-TaxID.py -i {id_list_F}  -l Family   -n {id_list3} --taxonomy {config.Kraken2_DATABASE}/Kraken2.Taxonomy.refseq_240720.txt -o TaxIDAbu.F
        {config.BIN_PATH}/BPTracer/Kraken2/kraken2-combineSample-TaxID.py -i {id_list_G}  -l Genus    -n {id_list3} --taxonomy {config.Kraken2_DATABASE}/Kraken2.Taxonomy.refseq_240720.txt -o TaxIDAbu.G
        {config.BIN_PATH}/BPTracer/Kraken2/kraken2-combineSample-TaxID.py -i {id_list_S}  -l Species  -n {id_list3} --taxonomy {config.Kraken2_DATABASE}/Kraken2.Taxonomy.refseq_240720.txt -o TaxIDAbu.S
        """)
        return cmd