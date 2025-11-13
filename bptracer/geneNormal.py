import subprocess
import textwrap
from bptracer import config
from bptracer.BaseRunner import BaseRunner

class SARGRunner(BaseRunner):
    def build_command(self):
        id = self.params.get('id')
        file1 = self.params.get('file1')

        cmd = textwrap.dedent(rf"""
        cd {config.OUTPUT_PATH}
        mkdir {id}
        cd {id}
        {config.SARG_MAPPING_SOFTWARE} -d {config.SARG_DATABASE} -q {file1} \
            -o {id}.m8  \
            -t ./ \
            -b 8 \
            -f {config.SARG_FORMAT} \
            --evalue {config.SARG_EVALUE} \
            -k {config.SARG_MAX_TARGET_SEQS} \

        perl {config.BIN_PATH}/best_m8.pl {id}.SARG.m8  > {id}.SARG.m8.fil
        perl {config.BIN_PATH}/add.m8.func.pl {id}.SARG.m8.fil  {config.SARG_DATABASE}/SARG.3.2.list  {file1} > {id}.SARG.anno.xls """)
        return cmd



