import subprocess
import textwrap
from bptracer import config
from bptracer.BaseRunner import BaseRunner

class SPAdesRunner(BaseRunner):
    def build_command(self):
        id = self.params.get('id')
        file1 = self.params.get('file1')
        file2 = self.params.get('file2')

        cmd = textwrap.dedent(rf"""
        cd {config.SPAdes_OUTPUT_PATH}
        python3 {config.SPAdes_MAPPING_SOFTWARE} --meta -t {config.SPAdes_THREADS} -m  {config.SPAdes_MEMORY}   --disable-gzip-output -1 {file1} -2 {file2} -o {id}
        perl {config.BIN_PATH}/BPTracer/renamefa.pl ./{id}/scaffolds.fasta {id} {id}.contig.ok.fa
        perl {config.BIN_PATH}/BPTracer/deal_fa.pl -format 3 {id}.contig.ok.fa | perl -e 'while(<>){{chomp;@a=split; if($a[1] > 10000){{$a[1]=10000;}} print "$a[0]\t$a[1]\n";}}' > {id}.contig.ok.fa.chrlist
        #perl {config.BIN_PATH}/BPTracer/fa_fq_len_bar.pl {id}.contig.ok.fa.chrlist {id}.contig.length.pdf contig
        rm -r {config.SPAdes_OUTPUT_PATH}/{id}/
        perl {config.BIN_PATH}/BPTracer/deal_fa.pl {id}.contig.ok.fa -len 2000 -format 6 -type 1 > {id}.contig.ok.2k.fa
        """)
        return cmd

import textwrap
from bptracer.BaseRunner import BaseRunner
# 不再强制 import 默认 config 模块，由调用者传入动态 config
# from bptracer import config  # 可以删掉


class AssemblyRunner(BaseRunner):
    """
    通用组装 Runner，根据 assembler 参数选择 MEGAHIT 或 SPAdes。

    期望参数（通过 BaseRunner.__init__ 传入）:
    - config    : 配置模块（由 BPtracer.main 动态 load_config_module 得到）
    - id        : 样本 ID
    - file1     : R1 FASTQ 路径
    - file2     : R2 FASTQ 路径
    - assembler : 'megahit' 或 'spades'（小写），默认使用 megahit
    """

    def build_command(self, **kwargs):
        # 优先使用 params 中的 config，其次允许从 kwargs 传入
        config = self.params.get("config") or kwargs.get("config")
        if config is None:
            raise ValueError("AssemblyRunner 需要 config 参数，但未提供。")

        sample_id = self.params.get("id")
        file1 = self.params.get("file1")
        file2 = self.params.get("file2")
        assembler = (self.params.get("assembler") or "megahit").lower()

        if not sample_id or not file1 or not file2:
            raise ValueError("AssemblyRunner 需要 id、file1、file2 三个基本参数。")

        if assembler == "megahit":
            cmd = textwrap.dedent(rf"""
            cd {config.Megahit_OUTPUT_PATH}
            {config.Megahit_MAPPING_SOFTWARE} \
                -1 {file1} -2 {file2} \
                --min-contig-len {config.Megahit_MIN_LENGTH} \
                -t {config.Megahit_THREADS} \
                -o ./{sample_id}
            perl {config.BIN_PATH}/BPTracer/renamefa.pl ./{sample_id}/final.contigs.fa {sample_id} {sample_id}.contig.ok.fa
            perl {config.BIN_PATH}/BPTracer/deal_fa.pl -format 3 {sample_id}.contig.ok.fa \
                | perl -e 'while(<>){{chomp;@a=split; if($a[1] > 10000){{$a[1]=10000;}} print "$a[0]\t$a[1]\n";}}' \
                > {sample_id}.contig.ok.fa.chrlist
            #perl {config.BIN_PATH}/BPTracer/fa_fq_len_bar.pl {sample_id}.contig.ok.fa.chrlist {sample_id}.contig.length.pdf contig
            rm -r {config.Megahit_OUTPUT_PATH}/{sample_id}/
            perl {config.BIN_PATH}/BPTracer/deal_fa.pl {sample_id}.contig.ok.fa -len 2000 -format 6 -type 1 > {sample_id}.contig.ok.2k.fa
            """).strip()

        elif assembler == "spades":
            cmd = textwrap.dedent(rf"""
            cd {config.SPAdes_OUTPUT_PATH}
            python3 {config.SPAdes_MAPPING_SOFTWARE} \
                --meta \
                -t {config.SPAdes_THREADS} \
                -m {config.SPAdes_MEMORY} \
                --disable-gzip-output \
                -1 {file1} -2 {file2} \
                -o {sample_id}
            perl {config.BIN_PATH}/BPTracer/renamefa.pl ./{sample_id}/scaffolds.fasta {sample_id} {sample_id}.contig.ok.fa
            perl {config.BIN_PATH}/BPTracer/deal_fa.pl -format 3 {sample_id}.contig.ok.fa \
                | perl -e 'while(<>){{chomp;@a=split; if($a[1] > 10000){{$a[1]=10000;}} print "$a[0]\t$a[1]\n";}}' \
                > {sample_id}.contig.ok.fa.chrlist
            #perl {config.BIN_PATH}/BPTracer/fa_fq_len_bar.pl {sample_id}.contig.ok.fa.chrlist {sample_id}.contig.length.pdf contig
            rm -r {config.SPAdes_OUTPUT_PATH}/{sample_id}/
            perl {config.BIN_PATH}/BPTracer/deal_fa.pl {sample_id}.contig.ok.fa -len 2000 -format 6 -type 1 > {sample_id}.contig.ok.2k.fa
            """).strip()
        else:
            raise ValueError(f"Unsupported assembler: {assembler}")

        return cmd
