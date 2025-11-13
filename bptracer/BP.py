import os
import textwrap
from bptracer.BaseRunner import BaseRunner
from bptracer.fileManager import mkdir
#from bptracer import config

# RawdataStat
class RawdataStat(BaseRunner):
    def build_command(self):
        config = self.params.get('config')
        id = self.params.get('id')
        file1 = self.params.get('file1')
        file2 = self.params.get('file2')

        cmd = textwrap.dedent(rf"""
        cd {config.BP_OUTPUT_PATH}; mkdir -p 00.DataStat/{id}; cd 00.DataStat/{id}
        
        {config.BP_FQ2FA_SOFTWARE} {file1} .//{id}_1.fa
        {config.BP_FQ2FA_SOFTWARE} {file2} .//{id}_2.fa
        # Using minimap2 to search 16s
        {config.BP_MINIMAP2} -ax sr {config.BP_16S_DATABASE} .//{id}_1.fa .//{id}_2.fa >.//{id}.sam
        
        # Using Diamond to search USCMGs  (Universal single-copy genes)
        {config.BP_USCMG_SOFTWARE} -q .//{id}_1.fa -d {config.BP_USCMG_DATABASE} -o .//{id}.uscmg_1.dmd -f tab  -p 20  -e 3 --id 0.45 --max-target-seqs 1
        {config.BP_USCMG_SOFTWARE} -q .//{id}_2.fa -d {config.BP_USCMG_DATABASE} -o .//{id}.uscmg_2.dmd -f tab  -p 20  -e 3 --id 0.45 --max-target-seqs 1
        cat .//{id}.uscmg_1.dmd .//{id}.uscmg_2.dmd > .//{id}.uscmg.blastx.txt
        
        # Obtain Metadata
        python3 {config.BIN_PATH}/BPTracer/ProcessMeta.py --indir ./ --outdir ./ --sample_id {id} --meta_data_out meta_data_online.txt  --coglist {config.BP_USCMG_LIST} --config {config.CONFIG_SCRIPT}
        """)
        return cmd


class GeneAnno(BaseRunner):
    def build_command(self):
        config = self.params.get('config')
        id = self.params.get('id')
        file1 = self.params.get('file1')
        file2 = self.params.get('file2')
        geneType = self.params.get('geneType')
        
        genePath, geneDBDiamond, geneDB , geneStructure  = get_gene_path(geneType,config)

        cmd = textwrap.dedent(rf"""
        cd {config.BP_OUTPUT_PATH}; mkdir -p {genePath}/{id}; cd {genePath}/{id}
        # 链接统计文件
        #find {config.BP_OUTPUT_PATH}/00.DataStat/{id}/ -type f ! -name "*.fq" ! -name "*.fastaq" ! -name "*.fq.gz" ! -name "*.fastaq.gz" -exec ln -s {{}} ./ \;
        
        # 功能基因比对
        {config.BP_DIAMOND_SOFTWARE} -d {geneDBDiamond} -q {config.BP_OUTPUT_PATH}/00.DataStat/{id}/{id}_1.fa -o .//{id}_1.us -e 10 -p 40 -k 1 --id 60
        {config.BP_DIAMOND_SOFTWARE} -d {geneDBDiamond} -q {config.BP_OUTPUT_PATH}/00.DataStat/{id}/{id}_2.fa -o .//{id}_2.us -e 10 -p 40 -k 1 --id 60
        {config.BP_EXTREA_SOFTWARE} .//{id}_1.us {config.BP_OUTPUT_PATH}/00.DataStat/{id}/{id}_1.fa .//{id}.extract_1.fa
        {config.BP_EXTREA_SOFTWARE} .//{id}_2.us {config.BP_OUTPUT_PATH}/00.DataStat/{id}/{id}_2.fa .//{id}.extract_2.fa
        
        # 初步抽取基因
        #python3 {config.BP_MERGEFA_SOFTWARE} ./ ./ meta-data.txt .//meta_data_online.txt .//extracted.fa  {config.BP_USCMG_LIST} --config {config.CONFIG_SCRIPT}
        #python3 {config.BP_MERGEFA_SOFTWARE} --indir {config.BP_OUTPUT_PATH}/00.DataStat/{id} --outdir ./ --sample_id {id} --meta_data_out meta_data_online.txt --extracted_fasta extracted.fa  --coglist {config.BP_USCMG_LIST} --config {config.CONFIG_SCRIPT}
        python3 {config.BIN_PATH}/BPTracer/MergeFastaRename.py  --outdir ./ --sample_id {id} --extracted_fasta extracted.fa
        """)
        return cmd
    
    
def get_gene_path(geneType, config):
    if geneType == "ARGs":
        genePath = "01.ARGs"
        geneDBDiamond = config.BP_ARG_DATABASE
        geneDB = config.BP_BLASTARG_DATABASE
        geneStructure = config.BP_ARG_STRUCTURE
    elif geneType == "MGEs":
        genePath = "02.MGEs"
        geneDBDiamond = config.BP_MGE_DATABASE
        geneDB = config.BP_BLASTMGE_DATABASE
        geneStructure = config.BP_MGE_STRUCTURE
    elif geneType == "MRGs":
        genePath = "03.MRGs"
        geneDBDiamond = config.BP_MRG_DATABASE
        geneDB = config.BP_BLASTMRG_DATABASE
        geneStructure = config.BP_MRG_STRUCTURE
    elif geneType == "VFs":
        genePath = "04.VFs"
        geneDBDiamond = config.BP_VFs_DATABASE
        geneDB = config.BP_BLASTVFs_DATABASE
        geneStructure = config.BP_VFs_STRUCTURE
    elif geneType == "SGs":
        genePath = "05.SGs"
        geneDBDiamond = config.BP_SGs_DATABASE
        geneDB = config.BP_BLASTSGs_DATABASE
        geneStructure = config.BP_SGs_STRUCTURE
    else:
        raise ValueError(f"Unsupported geneType: {geneType}")
    return genePath,geneDBDiamond, geneDB, geneStructure