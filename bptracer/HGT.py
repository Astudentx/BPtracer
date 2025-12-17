import subprocess
import textwrap
from bptracer.BaseRunner import BaseRunner

class HGTRunner(BaseRunner):
    def build_command(self):
        # 设置接口参数
        config = self.params.get('config')
        id = self.params.get('id')
        file1 = self.params.get('file1')
        length = self.params.get('length', 1000)

        filtered_contigs = f"{id}.filtered.fa"

        cmd = textwrap.dedent(rf"""
        cd {config.HGT_OUTPUT_PATH}; mkdir -p {id}; cd {id}
        python {config.FILTER_SOFTWARE} --input {file1} --output {filtered_contigs} --min-length {length}
        # Homology-based search with  waafle_search
        waafle_search {filtered_contigs} {config.BP_HGT_DATABASE}  --threads 60 --out {id}.blastout
        # Gene calling with waafle_genecaller
        waafle_genecaller {id}.blastout
        # Identify candidate LGT events with waafle_orgscorer
        waafle_orgscorer {filtered_contigs}  {id}.blastout {id}.gff {config.BP_HGT_STRUCTURE}
        # rm {id}.blastout {id}.gff
        """)
        return cmd
