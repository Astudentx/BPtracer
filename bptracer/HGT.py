import subprocess
import textwrap
from bptracer.BaseRunner import BaseRunner
import os

class HGTRunner(BaseRunner):
    def build_command(self):
        # 设置接口参数
        config = self.params.get('config')
        id = self.params.get('id')
        file1 = self.params.get('file1')

        cmd = textwrap.dedent(rf"""
        cd {config.HGT_OUTPUT_PATH}; mkdir -p {id}; cd {id}
        # Homology-based search with  waafle_search
        python {config.BIN_PATH}/WAAFLE/waafle/waafle_search.py {file1} {config.BP_HGT_DATABASE}  --threads 60 --out {id}.blastout
        # Gene calling with waafle_genecaller
        python {config.BIN_PATH}/WAAFLE/waafle/waafle_genecaller.py {id}.blastout
        # Identify candidate LGT events with waafle_orgscorer
        python {config.BIN_PATH}/WAAFLE/waafle/waafle_orgscorer.py {file1}  {id}.blastout {id}.gff {config.BP_HGT_STRUCTURE}
        # rm {id}.blastout {id}.gff
        """)
        return cmd