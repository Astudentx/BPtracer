import subprocess
import textwrap
from bptracer import config
from bptracer.BaseRunner import BaseRunner
class fq2fa(BaseRunner):
    def build_command(self):
        id = self.params.get('id')
        file1 = self.params.get('file1')
        file2 = self.params.get('file2')

        cmd = textwrap.dedent(rf"""
        cd {config.OUTPUT_PATH}
        cd geneNormal
        mkdir {id}; cd {id}
        seqtk seq -a {file1}  > {id}_1.fa
        seqtk seq -a {file2}  > {id}_2.fa
        
        # Using minimap2 to search 16s
        minimap2 -ax sr /mnt/sdc/zhangyz/bin/TAVMM/DB/gg85_yinxiaole.fasta.mmi  {id}_1.fa  {id}_2.fa > {id}.sam
        # Using Diamond to search USCMGs  (Universal single-copy genes)
        diamond blastx -q {id}_1.fa -d /mnt/sdc/zhangyz/bin/TAVMM/DB/KO30_DIAMOND.dmnd -o {id}.uscmg_1.dmd -f tab  -p 20  -e 3 --id 0.45 --max-target-seqs 1
        diamond blastx -q {id}_2.fa -d /mnt/sdc/zhangyz/bin/TAVMM/DB/KO30_DIAMOND.dmnd -o {id}.uscmg_2.dmd -f tab  -p 20  -e 3 --id 0.45 --max-target-seqs 1
        cat {id}.uscmg_1.dmd {id}.uscmg_2.dmd > .//{id}.uscmg.blastx.txt

        {config.SARG_MAPPING_SOFTWARE} -d {config.SARG_DATABASE} -q {file1} \
            -o {id}.m8  \
            -t ./ \
            -b 8 \
            -f {config.SARG_FORMAT} \
            --evalue {config.SARG_EVALUE} \
            -k {config.SARG_MAX_TARGET_SEQS}  """)
        return cmd
