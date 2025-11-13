import subprocess
import textwrap
from bptracer.BaseRunner import BaseRunner
import os

class FastqStatRunner(BaseRunner):
    def build_command(self):
        config = self.params.get('config')
        fqName = self.params.get('fqlist')   
        fqlist = os.path.realpath(fqName)
        statpath = os.path.join(config.OUTPUT_PATH,"FastqStat")
        cmd = textwrap.dedent(rf"""
        mkdir -p {statpath}
        cd {statpath}
        java -jar  {config.FASTQSTAT_SOFTWARE}/FastqStat.jar -i {fqlist}   > stat.main.xls
        python {config.Kraken2_MAPPING_SOFTWARE}/mybin/ProcessStat.py
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
        {config.Kraken2_MAPPING_SOFTWARE}/kraken2 --db {config.Kraken2_DATABASE} --threads {config.Kraken2_THREADS} --quick --report-zero-counts --gzip-compressed --paired --output {id}.readinfo --report {id}.report {file1} {file2}
        python {config.Kraken2_MAPPING_SOFTWARE}/kreport2mpa.py -r {id}.report -o {id}.mpa
        python {config.Kraken2_MAPPING_SOFTWARE}/est_abundance.py -t 1 -k {config.Kraken2_DATABASE}/database150mers.kmer_distrib -i {id}.report -o {id}.report.D -l D
        python {config.Kraken2_MAPPING_SOFTWARE}/est_abundance.py -t 1 -k {config.Kraken2_DATABASE}/database150mers.kmer_distrib -i {id}.report -o {id}.report.P -l P
        python {config.Kraken2_MAPPING_SOFTWARE}/est_abundance.py -t 1 -k {config.Kraken2_DATABASE}/database150mers.kmer_distrib -i {id}.report -o {id}.report.C -l C
        python {config.Kraken2_MAPPING_SOFTWARE}/est_abundance.py -t 1 -k {config.Kraken2_DATABASE}/database150mers.kmer_distrib -i {id}.report -o {id}.report.O -l O
        python {config.Kraken2_MAPPING_SOFTWARE}/est_abundance.py -t 1 -k {config.Kraken2_DATABASE}/database150mers.kmer_distrib -i {id}.report -o {id}.report.F -l F
        python {config.Kraken2_MAPPING_SOFTWARE}/est_abundance.py -t 1 -k {config.Kraken2_DATABASE}/database150mers.kmer_distrib -i {id}.report -o {id}.report.G -l G
        python {config.Kraken2_MAPPING_SOFTWARE}/est_abundance.py -t 1 -k {config.Kraken2_DATABASE}/database150mers.kmer_distrib -i {id}.report -o {id}.report.S -l S
        # rm {id}.readinfo {id}.report
        """)
        return cmd
    
    
class Kraken2Runner2(BaseRunner):
    def build_command(self):
        # 设置接口参数
        config = self.params.get('config')
        id_list = self.params.get('id_list')
        lineage = self.params.get('lineage', 'F')  # 新增lineage参数，默认值F

        
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
        python  {config.Kraken2_MAPPING_SOFTWARE}/combine_bracken_outputs.py --files {id_list_D} --names {id_list2} -o taxonomy.D
        python  {config.Kraken2_MAPPING_SOFTWARE}/combine_bracken_outputs.py --files {id_list_P} --names {id_list2} -o taxonomy.P
        python  {config.Kraken2_MAPPING_SOFTWARE}/combine_bracken_outputs.py --files {id_list_C} --names {id_list2} -o taxonomy.C
        python  {config.Kraken2_MAPPING_SOFTWARE}/combine_bracken_outputs.py --files {id_list_O} --names {id_list2} -o taxonomy.O
        python  {config.Kraken2_MAPPING_SOFTWARE}/combine_bracken_outputs.py --files {id_list_F} --names {id_list2} -o taxonomy.F
        python  {config.Kraken2_MAPPING_SOFTWARE}/combine_bracken_outputs.py --files {id_list_G} --names {id_list2} -o taxonomy.G
        python  {config.Kraken2_MAPPING_SOFTWARE}/combine_bracken_outputs.py --files {id_list_S} --names {id_list2} -o taxonomy.S

        # 界门纲目科属种复杂分析版本,需要stat.main.xls 
        # perl  {config.Kraken2_MAPPING_SOFTWARE}/mybin/kraken2-mergeStat-unclassfied-New.pl -prefix taxonomy -trim {trim_path}/stat.main.xls -tax {config.Kraken2_TAXLIST}  -out Final
        
        # 界门纲目科属种简单版本
        perl  {config.Kraken2_MAPPING_SOFTWARE}/mybin/kraken2-mergeStat-New.pl -prefix taxonomy -tax {config.Kraken2_TAXLIST}  -out TaxAbu
        """)
        
        if lineage != "F":
            cmd += textwrap.dedent(rf"""
        # TaxID合并版本分析
        #python  {config.Kraken2_MAPPING_SOFTWARE}/mybin/kraken2-combineSample-TaxID.py -i {id_list_D}  -l Kingdom  -n {id_list3} --taxonomy {config.Kraken2_DATABASE}/Kraken2.Taxonomy.refseq_240519.txt -o TaxIDAbu.D
        #python  {config.Kraken2_MAPPING_SOFTWARE}/mybin/kraken2-combineSample-TaxID.py -i {id_list_P}  -l Phylum   -n {id_list3} --taxonomy {config.Kraken2_DATABASE}/Kraken2.Taxonomy.refseq_240519.txt -o TaxIDAbu.P
        #python  {config.Kraken2_MAPPING_SOFTWARE}/mybin/kraken2-combineSample-TaxID.py -i {id_list_C}  -l Class    -n {id_list3} --taxonomy {config.Kraken2_DATABASE}/Kraken2.Taxonomy.refseq_240519.txt -o TaxIDAbu.C
        #python  {config.Kraken2_MAPPING_SOFTWARE}/mybin/kraken2-combineSample-TaxID.py -i {id_list_O}  -l Order    -n {id_list3} --taxonomy {config.Kraken2_DATABASE}/Kraken2.Taxonomy.refseq_240519.txt -o TaxIDAbu.O
        #python  {config.Kraken2_MAPPING_SOFTWARE}/mybin/kraken2-combineSample-TaxID.py -i {id_list_F}  -l Family   -n {id_list3} --taxonomy {config.Kraken2_DATABASE}/Kraken2.Taxonomy.refseq_240519.txt -o TaxIDAbu.F
        #python  {config.Kraken2_MAPPING_SOFTWARE}/mybin/kraken2-combineSample-TaxID.py -i {id_list_G}  -l Genus    -n {id_list3} --taxonomy {config.Kraken2_DATABASE}/Kraken2.Taxonomy.refseq_240519.txt -o TaxIDAbu.G
        #python  {config.Kraken2_MAPPING_SOFTWARE}/mybin/kraken2-combineSample-TaxID.py -i {id_list_S}  -l Species  -n {id_list3} --taxonomy {config.Kraken2_DATABASE}/Kraken2.Taxonomy.refseq_240519.txt -o TaxIDAbu.S

        python  {config.Kraken2_MAPPING_SOFTWARE}/mybin/kraken2-combineSample-TaxID.py -i {id_list_D}  -l Kingdom  -n {id_list3} --taxonomy {config.Kraken2_DATABASE}/Kraken2.Taxonomy.refseq_240720.txt -o TaxIDAbu.D
        python  {config.Kraken2_MAPPING_SOFTWARE}/mybin/kraken2-combineSample-TaxID.py -i {id_list_P}  -l Phylum   -n {id_list3} --taxonomy {config.Kraken2_DATABASE}/Kraken2.Taxonomy.refseq_240720.txt -o TaxIDAbu.P
        python  {config.Kraken2_MAPPING_SOFTWARE}/mybin/kraken2-combineSample-TaxID.py -i {id_list_C}  -l Class    -n {id_list3} --taxonomy {config.Kraken2_DATABASE}/Kraken2.Taxonomy.refseq_240720.txt -o TaxIDAbu.C
        python  {config.Kraken2_MAPPING_SOFTWARE}/mybin/kraken2-combineSample-TaxID.py -i {id_list_O}  -l Order    -n {id_list3} --taxonomy {config.Kraken2_DATABASE}/Kraken2.Taxonomy.refseq_240720.txt -o TaxIDAbu.O
        python  {config.Kraken2_MAPPING_SOFTWARE}/mybin/kraken2-combineSample-TaxID.py -i {id_list_F}  -l Family   -n {id_list3} --taxonomy {config.Kraken2_DATABASE}/Kraken2.Taxonomy.refseq_240720.txt -o TaxIDAbu.F
        python  {config.Kraken2_MAPPING_SOFTWARE}/mybin/kraken2-combineSample-TaxID.py -i {id_list_G}  -l Genus    -n {id_list3} --taxonomy {config.Kraken2_DATABASE}/Kraken2.Taxonomy.refseq_240720.txt -o TaxIDAbu.G
        python  {config.Kraken2_MAPPING_SOFTWARE}/mybin/kraken2-combineSample-TaxID.py -i {id_list_S}  -l Species  -n {id_list3} --taxonomy {config.Kraken2_DATABASE}/Kraken2.Taxonomy.refseq_240720.txt -o TaxIDAbu.S
        """)
        return cmd