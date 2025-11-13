#!/usr/bin/env python3
import sys
import os
import argparse

# ----------------------------------------------------------------------
# 基础路径与模块导入
# ----------------------------------------------------------------------

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# 若仍希望调试看路径，可以解开下一行
# print(BASE_DIR)

from bptracer.BaseRunner import BaseRunner
from bptracer import Kraken2
from bptracer import inputList
from bptracer import BP
from bptracer import BP2
from bptracer import HGT
from bptracer import Megahit
from bptracer import SPAdes
from bptracer import fileManager
from bptracer.tool import load_config_module
from bptracer import version


# ----------------------------------------------------------------------
# 子命令解析器工厂函数
# ----------------------------------------------------------------------

def add_subparser(
    subparsers,
    name: str,
    description: str,
    parents=None,
) -> argparse.ArgumentParser:
    """
    创建统一风格的子命令解析器：
    - RawDescriptionHelpFormatter 保留多行 description 的排版
    - help 使用 description 的第一行作为简要说明
    - parents 用于共享全局参数（如 --config, --auto-run 等）
    """
    short_help = description.strip().splitlines()[0]
    if parents is None:
        parents = []

    subpar = subparsers.add_parser(
        name,
        description=description,
        help=short_help,
        parents=parents,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    return subpar


# ----------------------------------------------------------------------
# 解析器构建
# ----------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    """构建顶层解析器与全部子命令解析器。"""

    # 全局父解析器：所有子命令共享这些参数
    global_parent = argparse.ArgumentParser(add_help=False)
    global_parent.add_argument(
        '--version',
        help='Show BP-Tracer version and exit.',
        action='version',
        version=version.__version__,
    )
    global_parent.add_argument(
        "--auto-run",
        action="store_true",
        help=(
            "Automatically execute all generated shell scripts in parallel and "
            "wait for them to finish. If not set, BPtracer only generates scripts."
        ),
    )
    global_parent.add_argument(
        "--max-workers",
        type=int,
        default=3,
        help=(
            "Maximum number of scripts to run in parallel when --auto-run is set. "
            "Default: 3."
        ),
    )
    global_parent.add_argument(
        "--config", "-c",
        type=str,
        default="bptracer.config",
        help=(
            "Configuration module or file to load. Accepts either a Python module "
            "path (e.g. 'bptracer.config') or a full filesystem path to a "
            "configuration script (e.g. '/path/to/BPtracer/bptracer/config.py'). "
            "If not specified, the default 'bptracer.config' is used."
        ),
    )

    # 主解析器（展示总体介绍与子命令列表）
    parser = argparse.ArgumentParser(
        prog="BPtracer",
        parents=[global_parent],
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=(
            "Core functions include:\n"
            "  * Taxonomic and pathogen profiling for metagenomic reads\n"
            "  * Detection of harmful gene types and hosts from reads\n"
            "  * Assembly and HGT analysis based on contigs\n"
        ),
    )

    subparsers = parser.add_subparsers(
        title="Sub-commands",
        dest="subparser_name",
        metavar="<command>",
    )

    # ---------------------- 子命令描述信息 ---------------------------

    BP_description = (
        "Trace harmful gene types and hosts for metagenomic samples (step 1).\n"
        "\n"
        "This subcommand performs sequences stat of raw reads, and\n"
        "annotation of antimicrobial resistance and other harmful genes.\n"
        "\n"
        "Example:\n"
        "  BPtracer BP --file paired_fastq_list.txt --pwd /path/to/output\n"
    )

    BP2_description = (
        "Trace harmful gene types and hosts for metagenomic samples (step 2).\n"
        "\n"
        "This subcommand processes BP-Tracer outputs to generate filtered functional\n"
        "gene sequences and summary tables for downstream analyses.\n"
        "\n"
        "Example:\n"
        "  BPtracer BP2 --file paired_fastq_list.txt --pwd /path/to/output\n"
    )

    Tax_description = (
        "Classify metagenomic reads using Kraken2.\n"
        "\n"
        "Reads are assigned to taxa based on k-mer profiles, enabling high-resolution\n"
        "taxonomic composition analysis.\n"
        "\n"
        "Example:\n"
        "  BPtracer Tax --file paired_fastq_list.txt --db BPTax_V2 --pwd /path/to/output\n"
    )

    Megahit_description = (
        "Assemble metagenomic reads using MEGAHIT.\n"
        "\n"
        "This subcommand assembles paired-end metagenomic FASTQ reads into contigs\n"
        "suitable for downstream annotation and HGT analysis.\n"
        "\n"
        "Example:\n"
        "  BPtracer Megahit --file paired_fastq_list.txt --pwd /path/to/output\n"
    )

    SPAdes_description = (
        "Assemble metagenomic reads using SPAdes.\n"
        "\n"
        "This subcommand assembles paired-end metagenomic FASTQ reads into\n"
        "high-quality contigs for downstream BP-Tracer analyses.\n"
        "\n"
        "Example:\n"
        "  BPtracer SPAdes --file paired_fastq_list.txt --pwd /path/to/output\n"
    )

    HGT_description = (
        "Detect horizontal gene transfer (HGT) events using WAAFLE.\n"
        "\n"
        "This subcommand identifies candidate lateral gene transfer (LGT) events\n"
        "from assembled metagenomes, including host–donor pairs.\n"
        "\n"
        "Input:\n"
        "  A list of single FASTA files containing assembled contigs.\n"
        "\n"
        "Example:\n"
        "  BPtracer HGT --file contig_fasta_list.txt --pwd /path/to/output\n"
    )

    # ---------------------- BP 子命令 ---------------------------

    bp_parser = add_subparser(subparsers, 'BP', BP_description, parents=[global_parent])
    bp_req = bp_parser.add_argument_group('required arguments')
    bp_req.add_argument(
        '--file', '-f',
        help="List file of paired-end metagenomic FASTQ reads.",
        required=True,
    )
    bp_req.add_argument(
        '--pwd', '-o',
        help="Output folder.",
        default="./",
    )
    bp_req.add_argument(
        '--print',
        choices=['T', 'F'],
        default='F',
        help="Print underlying commands (T) or not (F).",
    )
    bp_req.add_argument(
        '--GeneType', '-g',
        help="Gene types to analyze (e.g. 'ARGs,MGEs'). Default: 'ALL' (all types).",
        default='ALL',
    )

    # ---------------------- BP2 子命令 ---------------------------

    bp2_parser = add_subparser(subparsers, 'BP2', BP2_description, parents=[global_parent])
    bp2_req = bp2_parser.add_argument_group('required arguments')
    bp2_req.add_argument(
        '--file', '-f',
        help="List file of paired-end metagenomic FASTQ reads.",
        required=True,
    )
    bp2_req.add_argument(
        '--pwd', '-o',
        help="Output folder.",
        default="./",
    )
    bp2_req.add_argument(
        '--thread', '-t',
        type=int,
        help="Number of threads used in BLAST stage.",
        default=4,
    )
    bp2_req.add_argument(
        '--print',
        choices=['T', 'F'],
        default='F',
        help="Print underlying commands (T) or not (F).",
    )
    bp2_req.add_argument(
        '--GeneType', '-g',
        help="Gene types to analyze (e.g. 'ARGs,MGEs'). Default: 'ALL' (all types).",
        default='ALL',
    )

    # ---------------------- Tax 子命令（Kraken2）-------------------

    tax_parser = add_subparser(subparsers, 'Tax', Tax_description, parents=[global_parent])
    tax_req = tax_parser.add_argument_group('required arguments')
    tax_req.add_argument(
        '--file', '-f',
        help="List file of paired-end metagenomic FASTQ reads.",
        required=True,
    )
    tax_req.add_argument(
        '--db', '-d',
        help=(
            "Database for Kraken2 classification. Options: "
            "BPTax_V1, BPTax_V2, krakenDB-202212, krakenDB-202406."
        ),
        default="BPTax_V2",
    )
    tax_req.add_argument(
        '--pwd', '-o',
        help="Output folder.",
        default="./",
    )
    tax_req.add_argument(
        '--print',
        choices=['T', 'F'],
        default='F',
        help="Print underlying commands (T) or not (F).",
    )

    # ---------------------- SPAdes 子命令 -------------------------

    spades_parser = add_subparser(subparsers, 'SPAdes', SPAdes_description, parents=[global_parent])
    spades_req = spades_parser.add_argument_group('required arguments')
    spades_req.add_argument(
        '--file', '-f',
        help="List file of paired-end metagenomic FASTQ reads.",
        required=True,
    )
    spades_req.add_argument(
        '--pwd', '-o',
        help="Output folder.",
        default="./",
    )
    spades_req.add_argument(
        '--print',
        choices=['T', 'F'],
        default='F',
        help="Print underlying commands (T) or not (F).",
    )

    # ---------------------- Megahit 子命令 ------------------------

    megahit_parser = add_subparser(subparsers, 'Megahit', Megahit_description, parents=[global_parent])
    megahit_req = megahit_parser.add_argument_group('required arguments')
    megahit_req.add_argument(
        '--file', '-f',
        help="List file of paired-end metagenomic FASTQ reads.",
        required=True,
    )
    megahit_req.add_argument(
        '--pwd', '-o',
        help="Output folder.",
        default="./",
    )
    megahit_req.add_argument(
        '--print',
        choices=['T', 'F'],
        default='F',
        help="Print underlying commands (T) or not (F).",
    )

    # ---------------------- HGT 子命令 ----------------------------

    hgt_parser = add_subparser(subparsers, 'HGT', HGT_description, parents=[global_parent])
    hgt_req = hgt_parser.add_argument_group('required arguments')
    hgt_req.add_argument(
        '--file', '-f',
        help="List file of contig FASTA files (assembled contigs).",
        required=True,
    )
    hgt_req.add_argument(
        '--db', '-d',
        help=(
            "Database for HGT classification. Options: RefseqPan2, chocophlan2, "
            "UnigeneSet-waafledb.v1.fa, UnigeneSet-waafledb.v2.fa (from WAAFLE)."
        ),
        default="RefseqPan2",
    )
    hgt_req.add_argument(
        '--pwd', '-o',
        help="Output folder.",
        default="./",
    )
    hgt_req.add_argument(
        '--print',
        choices=['T', 'F'],
        default='F',
        help="Print underlying commands (T) or not (F).",
    )

    return parser


# ----------------------------------------------------------------------
# 配置加载与初始化
# ----------------------------------------------------------------------

def init_config(args):
    """
    加载配置模块并设置输出路径。
    要求配置模块中必须实现 set_output_path(pwd)。
    """
    if args.config:
        print(f"Load the configuration module specified by the user: {args.config}")
        cfg = load_config_module(args.config)
    else:
        print("Use the default configuration module: bptracer.config")
        cfg = load_config_module('bptracer.config')

    if cfg is None:
        raise ValueError("config is not initialized. Please check the load_config_module call!")

    if not hasattr(cfg, "set_output_path"):
        raise AttributeError(f"配置模块 {args.config} 中缺少 set_output_path 方法")

    cfg.set_output_path(args.pwd)
    print(f"Output path set to: {cfg.OUTPUT_PATH}")
    print("mkdir analysis folders (将在各子命令中按需具体创建)")
    return cfg


# ----------------------------------------------------------------------
# 各子命令的具体执行逻辑
# ----------------------------------------------------------------------

def run_bp(args, config):
    """
    BP 主流程（step 1）：
    S01_RawdataStat   : per-sample read QC / basic stats
    S02_GeneAnno      : per-sample, per-geneType annotation
    """

    fileManager.mkdir(config.SHELL_PATH)

    print(f"Shells set to: {config.SHELL_PATH}")
    print(f"Results set to: {config.BP_OUTPUT_PATH}")

    # 读取 fqlist
    dataList = inputList.read_paired_list(args.file)
    # 生成 inputlist 用于后续分析（保留原始文件名 'intput.list'）
    inputList.generate_inputlist(args.file, "intput.list", config.BP_OUTPUT_PATH)

    # 基因类型列表
    gene_types = (
        args.GeneType.split(',')
        if args.GeneType != 'ALL'
        else ['ARGs', 'MGEs', 'MRGs', 'VFs', 'SGs']
    )

    # ---- 分阶段列表 ----
    s01_scripts = []  # S01: RawdataStat
    s02_scripts = []  # S02: GeneAnno

    # ---------------------- S01: RawdataStat ----------------------
    for i in range(dataList.number):
        ID = dataList.id[i]
        file1 = dataList.file1[i]
        file2 = dataList.file2[i]

        soft_runner = BP.RawdataStat(config=config, id=ID, file1=file1, file2=file2)
        soft_runner.print_command(should_print=args.print)
        script_path = os.path.join(config.SHELL_PATH, f"BP.S01.RawStat.{ID}.sh")
        soft_runner.generate_script(script_path)
        s01_scripts.append(script_path)

    # ---------------------- S02: 各基因类型的注释 ----------------------
    for gtype in gene_types:
        for i in range(dataList.number):
            ID = dataList.id[i]
            file1 = dataList.file1[i]
            file2 = dataList.file2[i]

            soft_runner = BP.GeneAnno(
                config=config, id=ID, file1=file1, file2=file2, geneType=gtype
            )
            soft_runner.print_command(should_print=args.print)
            script_path = os.path.join(
                config.SHELL_PATH, f"BP.S02.{gtype}Anno.{ID}.sh"
            )
            soft_runner.generate_script(script_path)
            s02_scripts.append(script_path)

    # 返回有序 dict，main() 中将按键顺序依次执行各阶段
    return {
        "S01_RawdataStat": s01_scripts,
        "S02_GeneAnno": s02_scripts,
    }


def run_bp2(args, config):
    """
    BP2 后处理流程（step 2）：
    S03_ExtractAndBlast : split fasta & run BLAST in chunks
    S04_MergeBlast      : merge BLAST results per geneType
    """

    gene_types = (
        args.GeneType.split(',')
        if args.GeneType != 'ALL'
        else ['ARGs', 'MGEs', 'MRGs', 'VFs', 'SGs']
    )

    if args.print == 'T':
        print("This message is printed because --print=T")
    else:
        print("Printing is disabled because --print=F")

    # 分阶段脚本列表
    s03_scripts = []  # S03: 分块 BLAST（BP.S03.temp.*.sh）
    s04_scripts = []  # S04: 合并 BLAST 结果（BP.S04.{gtype}.Merge.sh）

    for gtype in gene_types:
        print(f"Processing gene type: {gtype}")

        # 1) ExtractedFaFiles：分割 fasta 并生成对应脚本（S03）
        soft_runner = BP2.ExtractedFaFiles(
            config=config, geneType=gtype, thread=args.thread
        )
        soft_runner.process_files()

        for i, split_fa in enumerate(soft_runner.split_fa):
            soft_runner.build_command(index=i)
            soft_runner.print_command(should_print=args.print, index=i)

            script_path = os.path.join(
                config.SHELL_PATH, f"BP.S03.temp.{gtype}.{i}.sh"
            )
            soft_runner.generate_script(script_path, index=i)
            s03_scripts.append(script_path)
            print(f"Generated script for file {split_fa}: {script_path}")

        # 2) CatBlastFiles：合并 BLAST 结果（S04）
        soft_runner = BP2.CatBlastFiles(config=config, geneType=gtype)
        soft_runner.process_files()
        soft_runner.build_command()
        soft_runner.print_command(should_print=args.print)
        merge_script = os.path.join(config.SHELL_PATH, f"BP.S04.{gtype}.Merge.sh")
        soft_runner.generate_script(merge_script)
        s04_scripts.append(merge_script)

    # 返回分阶段结构，交给 main() 做按阶段顺序的 auto-run
    return {
        "S03_ExtractAndBlast": s03_scripts,
        "S04_MergeBlast": s04_scripts,
    }


def run_tax(args, config):
    """
    Kraken2 单独使用（Tax 子命令）：
    S00_FastqStat : per-sample read count / basic stats
    S01_Kraken2   : per-sample taxonomic classification
    S02_Merge     : merge classification outputs
    """

    fileManager.mkdir(config.SHELL_PATH)
    fileManager.mkdir(config.Kraken2_OUTPUT_PATH)

    config.set_kraken2_database(args.db)
    print(f"Output set to: {config.OUTPUT_PATH}")
    print(f"Shells set to: {config.SHELL_PATH}")
    print(f"Results set to: {config.Kraken2_OUTPUT_PATH}")
    print(f"Database set to: {config.Kraken2_DATABASE}")

    dataList = inputList.read_paired_list(args.file)

    # S00：统计每个样品的 reads 数量
    s00_scripts = []
    soft_runner = Kraken2.FastqStatRunner(config=config, fqlist=args.file)
    soft_runner.print_command(should_print=args.print)
    stat_script = os.path.join(config.SHELL_PATH, "Tax.S00.Stat.sh")
    soft_runner.generate_script(stat_script)
    s00_scripts.append(stat_script)

    # S01：每个样品的 Kraken2 分类
    s01_scripts = []
    for i in range(dataList.number):
        ID = dataList.id[i]
        file1 = dataList.file1[i]
        file2 = dataList.file2[i]

        soft_runner = Kraken2.Kraken2Runner(
            config=config, id=ID, file1=file1, file2=file2
        )
        soft_runner.print_command(should_print=args.print)
        script_path = os.path.join(config.SHELL_PATH, f"Tax.S01.Kraken2.{ID}.sh")
        soft_runner.generate_script(script_path)
        s01_scripts.append(script_path)

    # S02：合并 Kraken2 结果
    s02_scripts = []
    soft_runner = Kraken2.Kraken2Runner2(config=config, id_list=dataList.id)
    soft_runner.print_command(should_print=args.print)
    merge_script = os.path.join(config.SHELL_PATH, "Tax.S02.Kraken2.Merge.sh")
    soft_runner.generate_script(merge_script)
    s02_scripts.append(merge_script)

    # 返回分阶段 dict
    return {
        "S00_FastqStat": s00_scripts,
        "S01_Kraken2": s01_scripts,
        "S02_Merge": s02_scripts,
    }


def run_spades(args, config):
    """SPAdes 组装脚本生成（单阶段，每个样品一个脚本）。"""

    fileManager.mkdir(config.SHELL_PATH)
    fileManager.mkdir(config.SPAdes_OUTPUT_PATH)

    print(f"Shells set to: {config.SHELL_PATH}")
    print(f"Results set to: {config.SPAdes_OUTPUT_PATH}")

    dataList = inputList.read_paired_list(args.file)

    all_scripts = []
    for i in range(dataList.number):
        ID = dataList.id[i]
        file1 = dataList.file1[i]
        file2 = dataList.file2[i]

        soft_runner = SPAdes.SPAdesRunner(
            config=config, id=ID, file1=file1, file2=file2
        )
        soft_runner.print_command(should_print=args.print)
        script_path = os.path.join(
            config.SHELL_PATH, f"SPAdes.S01.Assambly.{ID}.sh"
        )
        soft_runner.generate_script(script_path)
        all_scripts.append(script_path)

    return all_scripts


def run_megahit(args, config):
    """Megahit 组装脚本生成（单阶段，每个样品一个脚本）。"""

    fileManager.mkdir(config.SHELL_PATH)
    fileManager.mkdir(config.Megahit_OUTPUT_PATH)

    print(f"Shells set to: {config.SHELL_PATH}")
    print(f"Results set to: {config.Megahit_OUTPUT_PATH}")

    dataList = inputList.read_paired_list(args.file)

    all_scripts = []
    for i in range(dataList.number):
        ID = dataList.id[i]
        file1 = dataList.file1[i]
        file2 = dataList.file2[i]

        soft_runner = Megahit.MegahitRunner(
            config=config, id=ID, file1=file1, file2=file2
        )
        soft_runner.print_command(should_print=args.print)
        script_path = os.path.join(
            config.SHELL_PATH, f"Megahit.S01.Assambly.{ID}.sh"
        )
        soft_runner.generate_script(script_path)
        all_scripts.append(script_path)

    return all_scripts


def run_hgt(args, config):
    """HGT 检测脚本生成（单阶段，每个 contig 集合一个脚本）。"""

    fileManager.mkdir(config.SHELL_PATH)
    fileManager.mkdir(config.HGT_OUTPUT_PATH)

    config.set_HGT_database(args.db)
    print(f"Output set to: {config.OUTPUT_PATH}")
    print(f"Shells set to: {config.SHELL_PATH}")
    print(f"Results set to: {config.HGT_OUTPUT_PATH}")
    print(f"Database set to: {config.BP_HGT_DATABASE}")
    print(f"Structure set to: {config.BP_HGT_STRUCTURE}")

    dataList = inputList.read_single_list(args.file)

    all_scripts = []
    for i in range(dataList.number):
        ID = dataList.id[i]
        file1 = dataList.file1[i]

        soft_runner = HGT.HGTRunner(config=config, id=ID, file1=file1)
        soft_runner.print_command(should_print=args.print)
        script_path = os.path.join(
            config.SHELL_PATH, f"HGT.S01.{args.db}.{ID}.sh"
        )
        soft_runner.generate_script(script_path)
        all_scripts.append(script_path)

    return all_scripts


# ----------------------------------------------------------------------
# 主入口
# ----------------------------------------------------------------------

def main():
    parser = build_parser()

    # 无参数时打印欢迎信息与总帮助
    if len(sys.argv) == 1:
        print("-----------------------------------------------")
        print('.....::: Welcome to trace gene hosts :::.....')
        print()
        fileManager.generate_header_bptracer2()
        print()
        print('.....::: BPtracer :::.....')
        print("version ：", version.__version__, sep="")
        print("author  ：", version.__author__, sep="")
        print("email   ：", version.__email__, sep="")
        print("-----------------------------------------------")
        print()
        print('General usage:')
        parser.print_help()
        sys.exit(0)

    args = parser.parse_args()

    if args.subparser_name is None:
        # 有参数但没指定子命令的情况
        parser.print_help()
        sys.exit(1)

    # args 已包含子命令参数，因此有 args.pwd
    config = init_config(args)

    # 根据子命令分发，返回脚本列表或“阶段 -> 脚本列表”的 dict
    scripts = []
    if args.subparser_name == 'BP':
        scripts = run_bp(args, config)
    elif args.subparser_name == 'BP2':
        scripts = run_bp2(args, config)
    elif args.subparser_name == 'Tax':
        scripts = run_tax(args, config)
    elif args.subparser_name == 'SPAdes':
        scripts = run_spades(args, config)
    elif args.subparser_name == 'Megahit':
        scripts = run_megahit(args, config)
    elif args.subparser_name == 'HGT':
        scripts = run_hgt(args, config)
    else:
        parser.print_help()
        sys.exit(1)

    # 如果开启 auto-run，则执行已生成脚本
    if args.auto_run and scripts:
        runner = BaseRunner()

        # 情况 1：普通子命令，返回的是 List[str]，当成单阶段处理
        if isinstance(scripts, list):
            print(f"[auto-run] Running {len(scripts)} scripts in parallel...")
            runner.run_scripts_parallel(scripts, max_workers=args.max_workers)
            print("[auto-run] All scripts finished.")

        # 情况 2：多阶段子命令（BP、BP2、Tax），返回的是 Dict[str, List[str]]
        elif isinstance(scripts, dict):
            # 利用 dict 的插入顺序：按返回时的顺序依次执行各阶段
            for stage_name, stage_scripts in scripts.items():
                if not stage_scripts:
                    continue
                print(f"[auto-run] {stage_name}: running {len(stage_scripts)} scripts in parallel...")
                runner.run_scripts_parallel(stage_scripts, max_workers=args.max_workers)
                print(f"[auto-run] {stage_name} finished.")

            print("[auto-run] All stages finished.")


if __name__ == '__main__':
    main()
