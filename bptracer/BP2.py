
import subprocess
import textwrap
from bptracer.BaseRunner import BaseRunner
import os
import pandas as pd
import glob


def get_gene_path(geneType, config):
    if geneType == "ARGs":
        genePath = "01.ARGs"
        geneDB = config.BP_BLASTARG_DATABASE
        geneStructure = config.BP_ARG_STRUCTURE
    elif geneType == "MGEs":
        genePath = "02.MGEs"
        geneDB = config.BP_BLASTMGE_DATABASE
        geneStructure = config.BP_MGE_STRUCTURE
    elif geneType == "MRGs":
        genePath = "03.MRGs"
        geneDB = config.BP_BLASTMRG_DATABASE
        geneStructure = config.BP_MRG_STRUCTURE
    elif geneType == "VFs":
        genePath = "04.VFs"
        geneDB = config.BP_BLASTVFs_DATABASE
        geneStructure = config.BP_VFs_STRUCTURE
    elif geneType == "SGs":
        genePath = "05.SGs"
        geneDB = config.BP_BLASTSGs_DATABASE
        geneStructure = config.BP_SGs_STRUCTURE
    else:
        raise ValueError(f"Unsupported geneType: {geneType}")
    return genePath, geneDB, geneStructure


        
class ExtractedFaFiles(BaseRunner):
    def process_files(self):
        config = self.params.get('config')
        geneType = self.params.get('geneType')
        thread = self.params.get('thread')
        genePath, geneDB, geneStructure  = get_gene_path(geneType,config)
        
        #config.SHELL_PATH
        #config.BP_OUTPUT_PATH
        #config.BP_BLAST_SOFTWARE
        #config.BP_EXTRACTEDFA_WINDOW
        #config.BP_BLASTARG_DATABASE
        
        # 设定Gene种类以及输出路径
        final_extracted_path = os.path.join(config.BP_OUTPUT_PATH,genePath)
        final_extracted_file = os.path.join(final_extracted_path,"Final.extracted.fa")
        
        # 合并所有 extracted.fa 文件.
        with open(final_extracted_file, "w") as final_out:
            for filepath in glob.glob(os.path.join(final_extracted_path, "**/extracted.fa"), recursive=True):
                with open(filepath, "r") as infile:
                    for line in infile:
                        final_out.write(line)
        print(f"所有{genePath}中的 extracted.fa 文件已合并到 {final_extracted_file}")
        
        
        # 分割 Final.extracted.fa 文件
        self.split_fa = []
        self.split_m8 = []
        with open(final_extracted_file, "r") as infile:
            sequence_counter = 0
            file_counter = 0
            split_file = None
            
            for line in infile:
                if line.startswith(">"):  # 序列 ID
                    if sequence_counter %  config.BP_EXTRACTEDFA_WINDOW == 0:
                        # 关闭之前的分割文件
                        if split_file:
                            split_file.close()
                        
                        # 创建新的分割文件, 并将内容保存到全局变量中
                        split_fa = os.path.join(final_extracted_path, f"temp.{file_counter}.fa")
                        split_m8 = os.path.join(final_extracted_path, f"temp.{file_counter}.fa.m8")
                        self.split_fa.append(split_fa)
                        self.split_m8.append(split_m8)
                        
                        split_file = open(split_fa, "w")
                        file_counter += 1
                    sequence_counter += 1
                split_file.write(line)
            if split_file:
                split_file.close()
        print(f"文件已分割为 {file_counter} 个部分，每部分最多包含 {config.BP_EXTRACTEDFA_WINDOW} 序列。")
        
        # 输出文件路径
        output_file = os.path.join(final_extracted_path,f"Final.{geneType}.m8.list")

        # 将路径逐行写入文件
        with open(output_file, "w") as f:
            for path in self.split_m8:
                f.write(path + "\n")
        print(f"所有 {geneType}.m8 文件路径已保存到 {output_file}")
        
        
        
        # 定义全局变量
        self.final_extracted_path = final_extracted_path
        self.final_extracted_file = final_extracted_file
        self.file_counter = file_counter
    
    def build_command(self, index):
        """生成针对单个分割文件的命令。"""
        config = self.params.get('config')
        geneType = self.params.get('geneType')
        thread = self.params.get('thread')
        genePath, geneDB, _ = get_gene_path(geneType, config)
        
        
        split_fa = self.split_fa[index]
        split_m8 = self.split_m8[index]
        #output_m8 = os.path.join(self.final_extracted_path, f"temp.{index}.fa.m8")
        cmd = textwrap.dedent(rf"""
        cd {self.final_extracted_path}
        {config.BP_BLAST_SOFTWARE} -query {split_fa} -out {split_m8} -db {geneDB} -evalue 1e-7 -num_threads {thread} -outfmt 6 -max_target_seqs 1
        """).strip()
        return cmd



#class CatBlastFiles(BaseRunner):
#    def build_command(self):
#        config = self.params.get('config')
#        geneType = self.params.get('geneType')
#        genePath, geneDB, geneStructure  = get_gene_path(geneType,config)
        
#        script_path = os.path.join(config.SHELL_PATH, f"S04.{geneType}_merge.sh")
#        final_extracted_path = os.path.join(config.BP_OUTPUT_PATH, genePath)
#        final_output_file = os.path.join(config.BP_OUTPUT_PATH, genePath, f"Final.{geneType}.blast.m8")
#        output_m8_list_path = os.path.join(config.BP_OUTPUT_PATH, genePath, f"Final.{geneType}.m8.list")
#        # 读取 m8 文件列表 (无标题文件)
#        try:
#            m8_list = pd.read_csv(output_m8_list_path, sep="\t", header=None)  # 无标题时 header=None
#        except Exception as e:
#            raise FileNotFoundError(f"无法读取 {output_m8_list_path} 文件: {e}")
        
#                # 获取所有路径
#        m8_paths = m8_list[0].tolist()

#        # 检查路径有效性
#        for path in m8_paths:
#            if not os.path.exists(path):
#                raise FileNotFoundError(f"文件 {path} 不存在，请检查 {output_m8_list_path}。")
        
        
#        # 生成合并脚本
#        with open(script_path, "w", encoding="utf-8") as script_file:
#            script_file.write(f"cd  {final_extracted_path}\n")
#            # 循环写成cat脚本
#            for idx, m8_path in enumerate(m8_paths):
#                if idx == 0:  # 第一个文件，使用 >
#                    script_file.write(f"cat {m8_path} > {final_output_file}\n")
#                else:  # 其余文件，使用 >>
#                    script_file.write(f"cat {m8_path} >> {final_output_file}\n")
                    
            
#            cmd1 = textwrap.dedent(rf"""
#            python3 {config.BIN_PATH}/BPTracer/MergeMeta.py \
#                -p {config.BP_OUTPUT_PATH}/{genePath}  \
#                -n meta_data_online.txt \
#                -o Final.meta_data_online.txt
#            """).strip()  # 删除可能多余的空白行
                        
#            cmd2 = textwrap.dedent(rf"""
#            python3 {config.BIN_PATH}/BPTracer/GeneAbundance.py \
#                -i {final_output_file} \
#                -m Final.meta_data_online.txt \
#                -p OUT.{geneType} \
#                -db {geneDB} \
#                -s {geneStructure} \
#                -o {final_extracted_path} 
#            """).strip()  # 删除可能多余的空白行
            

#            script_file.write(cmd1 + "\n")  # 确保每一行都以换行符结束
#            script_file.write(cmd2 + "\n")  # 确保每一行都以换行符结束
        
#        print(f"合并脚本已生成: {script_path}")
#        print(f"目标合并文件: {final_output_file}")
        
#        # 返回生成的脚本路径
#        return f"bash {script_path}"

class CatBlastFiles(BaseRunner):
    def process_files(self):
        """处理 m8 文件列表，检查路径有效性"""
        config = self.params.get('config')
        geneType = self.params.get('geneType')
        genePath, geneDB, geneStructure = get_gene_path(geneType, config)

        # 初始化路径
        self.final_extracted_path = os.path.join(config.BP_OUTPUT_PATH, genePath)
        self.final_output_file = os.path.join(self.final_extracted_path, f"Final.{geneType}.blast.m8")
        self.output_m8_list_path = os.path.join(self.final_extracted_path, f"Final.{geneType}.m8.list")
        self.script_path = os.path.join(config.SHELL_PATH, f"S04.{geneType}_merge.sh")

        # 读取 m8 文件列表
        try:
            m8_list = pd.read_csv(self.output_m8_list_path, sep="\t", header=None)
        except Exception as e:
            raise FileNotFoundError(f"无法读取 {self.output_m8_list_path} 文件: {e}")

        # 获取所有路径
        self.m8_paths = m8_list[0].tolist()

        ## 检查路径有效性
        #for path in self.m8_paths:
        #    if not os.path.exists(path):
        #        print FileNotFoundError(f"文件 {path} 不存在，请检查 {self.output_m8_list_path}。")
        #print(f"m8 文件列表已验证，共有 {len(self.m8_paths)} 个文件。")

    def build_command(self):
        """生成所有的命令并返回列表"""
        config = self.params.get('config')
        geneType = self.params.get('geneType')
        genePath, geneDB, geneStructure = get_gene_path(geneType, config)

        # 确保 process_files 已执行
        if not hasattr(self, 'm8_paths') or not self.m8_paths:
            raise RuntimeError("process_files 方法尚未执行，无法生成命令。")

        # 合并命令列表
        cmd = [f"cd {self.final_extracted_path}"]

        # 合并 m8 文件的命令
        for idx, m8_path in enumerate(self.m8_paths):
            if idx == 0:  # 第一个文件，使用 >
                cmd.append(f"cat {m8_path} > {self.final_output_file}")
            else:  # 其余文件，使用 >>
                cmd.append(f"cat {m8_path} >> {self.final_output_file}")

        # 添加后续 Python 脚本命令
        cmd.append(textwrap.dedent(rf"""
        # 合并 00.DataStat 文件夹中的所有元数据文件，生成最终的元数据文件
        # -p: 指定输入文件夹路径
        # -n: 指定元数据文件名
        # -o: 指定输出文件名
        python3 {config.BIN_PATH}/BPTracer/MergeMeta.py -p {config.BP_OUTPUT_PATH}/00.DataStat -n meta_data_online.txt  -o Final.meta_data_online.txt

        # 根据 BLAST 结果过滤功能基因的 FASTA 文件和 m8比对文件
        # -m8: 输入 BLAST 结果文件（m8 格式）
        # -fa: 输入提取的 FASTA 文件
        # -o_m8: 输出过滤后的 BLAST 结果文件
        # -o_fa: 输出过滤后的 FASTA 文件
        # -l: 过滤阈值（最小长度）
        # -id: 过滤阈值（最小相似度）
        # -e: 过滤阈值（最大 E 值）
        python3 {config.BIN_PATH}/BPTracer/FilterFasta.py  -m8 {self.final_extracted_path}/Final.{geneType}.blast.m8 -fa {self.final_extracted_path}/Final.extracted.fa -o_m8 {self.final_extracted_path}/Final.{geneType}.blast.m8.fil -o_fa {self.final_extracted_path}/Final.extracted.fa.fil  -l {config.BP_LENGTH_THRESHOLD} -id {config.BP_IDENTITY_THRESHOLD} -e {config.BP_EVALUE_THRESHOLD}
        """).strip())

        cmd.append(textwrap.dedent(rf"""
                                   
        # 计算功能基因的丰度
        # -i: 输入文件路径
        # -m: 元数据文件路径
        # -p: 输出文件前缀
        # -db: 基因数据库路径
        # -s: 基因结构文件路径
        # -o: 输出文件夹路径
        # -l: 过滤阈值（最小长度）
        # -id: 过滤阈值（最小相似度）
        # -e: 过滤阈值（最大 E 值）
        python3 {config.BIN_PATH}/BPTracer/GeneAbundance.py \
            -i {self.final_output_file} \
            -m Final.meta_data_online.txt \
            -p OUT.{geneType} \
            -db {geneDB} \
            -s {geneStructure} \
            -o {self.final_extracted_path} \
            -l {config.BP_LENGTH_THRESHOLD} \
            -id {config.BP_IDENTITY_THRESHOLD} \
            -e   {config.BP_EVALUE_THRESHOLD}
        """).strip())
        
        cmd.append(textwrap.dedent(rf"""
        # ppm
        python3 {config.BIN_PATH}/BPTracer/GenerateSubTable.py --input  {self.final_extracted_path}/OUT.{geneType}.ppm.txt --output  {self.final_extracted_path}/OUT.{geneType}.ppm.Type.txt --group_by Type
        python3 {config.BIN_PATH}/BPTracer/GenerateSubTable.py --input  {self.final_extracted_path}/OUT.{geneType}.ppm.txt --output  {self.final_extracted_path}/OUT.{geneType}.ppm.Subtype.txt --group_by Subtype
        # 16s
        python3 {config.BIN_PATH}/BPTracer/GenerateSubTable.py --input  {self.final_extracted_path}/OUT.{geneType}.16s.txt --output  {self.final_extracted_path}/OUT.{geneType}.16s.Type.txt --group_by Type
        python3 {config.BIN_PATH}/BPTracer/GenerateSubTable.py --input  {self.final_extracted_path}/OUT.{geneType}.16s.txt --output  {self.final_extracted_path}/OUT.{geneType}.16s.Subtype.txt --group_by Subtype
        # cellNumber
        python3 {config.BIN_PATH}/BPTracer/GenerateSubTable.py --input  {self.final_extracted_path}/OUT.{geneType}.cell_number.txt --output  {self.final_extracted_path}/OUT.{geneType}.cell_number.Type.txt --group_by Type
        python3 {config.BIN_PATH}/BPTracer/GenerateSubTable.py --input  {self.final_extracted_path}/OUT.{geneType}.cell_number.txt --output  {self.final_extracted_path}/OUT.{geneType}.cell_number.Subtype.txt --group_by Subtype
        
        # TaxSource
        python3 {config.BIN_PATH}/BPTracer/GeneAddTax.py  {config.BP_TAX_DATABASE} {self.final_extracted_path}/OUT.{geneType}.ppm.txt  {self.final_extracted_path}/Tax.{geneType}.ppm.txt
        python3 {config.BIN_PATH}/BPTracer/GenerateTaxTable.py  -i {self.final_extracted_path}/Tax.{geneType}.ppm.txt -p Tax.{geneType}
        """).strip())
                
        return cmd

