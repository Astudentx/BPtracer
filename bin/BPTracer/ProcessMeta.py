import os
import sys
import subprocess
import importlib.util
import argparse

def load_config_module(config_name_or_path):
    """
    动态加载配置模块，支持模块名（如 bptracer.config_custom）和文件路径（如 /path/to/config.py）。
    """
    if os.path.isfile(config_name_or_path):
        print(f"从文件路径加载配置模块: {config_name_or_path}")
        spec = importlib.util.spec_from_file_location("custom_config", config_name_or_path)
        if spec is None:
            raise ImportError(f"无法加载配置文件: {config_name_or_path}")
        module = importlib.util.module_from_spec(spec)
        sys.modules["custom_config"] = module
        spec.loader.exec_module(module)
        return module
    else:
        print(f"从模块名加载配置模块: {config_name_or_path}")
        try:
            return importlib.import_module(config_name_or_path)
        except ModuleNotFoundError as e:
            raise ImportError(f"无法加载配置模块 '{config_name_or_path}': {e}")

def read_metadata(sample_id, meta_data_out, default_library_size):
    """
    根据输入的样品 ID 生成元数据文件，并返回相关数据结构。
    
    参数:
    - sample_id: 样品 ID。
    - meta_data_out: 输出的元数据文件路径。
    - default_library_size: 强制定义的库大小，默认为 300。
    
    返回:
    - sampleid: 样品 ID 到样品名称的映射。
    - metainfo: 样品 ID 到元数据行的映射。
    - samplerlen: 样品 ID 到库大小的映射。
    """
    sampleid = {}
    metainfo = {}
    samplerlen = {}
    # 检查是否存在 meta_data_online.txt 文件，如果存在则重新生成
    if os.path.exists(meta_data_out):
        print(f"{meta_data_out} 已存在，将覆盖重新生成...")
    else:
        print(f"{meta_data_out} 不存在，将创建新的文件...")

    with open(meta_data_out, 'w') as meta_out:
        # 写入列头
        meta_out.write("SampleID\tName\tLibrarySize\t#ofReads\t#of16Sreads\tCellNumber\n")

        # 使用传入的样品 ID 生成元数据
        sample_name = f"{sample_id}"
        library_size = default_library_size  # 使用默认库大小

        # 更新数据结构
        sampleid[str(sample_id)] = sample_name
        samplerlen[str(sample_id)] = library_size
        metainfo[str(sample_id)] = f"{sample_id}\t{sample_name}\t{library_size}"

        # 写入到文件
        meta_out.write(f"{metainfo[str(sample_id)]}\t\n")

    return sampleid, metainfo, samplerlen

def parse_coglist(coglist):
    seq2OGs = {}
    seqlen = {}
    with open(coglist, 'r') as f:
        for line in f:
            tem = line.strip().split("\t")
            if len(tem) >= 3 and tem[0] and tem[1] and tem[2].isdigit():
                seq2OGs[tem[0]] = tem[1]
                seqlen[tem[0]] = int(tem[2])
    return seq2OGs, seqlen

def count_reads(indir, sample):
    file1 = os.path.join(indir, f"{sample}_1.fa")
    file2 = os.path.join(indir, f"{sample}_2.fa")
    if os.path.exists(file1) and os.path.exists(file2):
        num1 = int(subprocess.getoutput(f"grep '>' {file1} -c"))
        num2 = int(subprocess.getoutput(f"grep '>' {file2} -c"))
        return num1 + num2
    else:
        raise RuntimeError(f"Input files missing for sample {sample}!")

def count_16s_reads(indir, sample, samplerlen, config):
    sam_file = os.path.join(indir, f"{sample}.sam")
    if os.path.exists(sam_file):
        num_16s = int(subprocess.getoutput(f"{config.BP_SAMTOOLS_SOFTWARE} view -f 3 {sam_file} | wc -l"))
        # 保留12位小数
        return round(num_16s * samplerlen[sample] / 1432, 12)
    else:
        raise RuntimeError(f"SAM file missing for sample {sample}!")

def estimate_cell_number(indir, outdir, sample, seq2OGs, seqlen):
    blastx_file = os.path.join(indir, f"{sample}.uscmg.blastx.txt")
    ko_averagecov_file = os.path.join(outdir, f"{sample}.uscmg.ko_averagecov.txt")

    if os.path.exists(blastx_file):
        seqcov = {}
        with open(blastx_file, 'r') as f:
            for line in f:
                tem = line.strip().split("\t")
                seqcov[tem[1]] = seqcov.get(tem[1], 0) + float(tem[3])

        kocov = {}
        for sid, coverage in seqcov.items():
            if sid in seq2OGs:
                og = seq2OGs[sid]
                if og not in kocov:
                    kocov[og] = {}
                kocov[og][sid] = kocov[og].get(sid, 0) + coverage

        avgKOcopy = 0
        KOcount = 0
        with open(ko_averagecov_file, 'w') as ko_out:
            for og, seq_coverage in kocov.items():
                seqnum = len(seq_coverage)
                ave = sum(cov / seqlen[sid] for sid, cov in seq_coverage.items())
                ko_out.write(f"{og}\t{ave:.6f}\t{seqnum}\n")
                avgKOcopy += ave
                KOcount += 1

        if KOcount == 0:
            raise RuntimeError("No KO mapping found!")
        
        # 保留12位小数
        return round(avgKOcopy / KOcount, 12)
    else:
        raise RuntimeError("BLASTx file missing!")

def update_metadata(meta_data_out, metainfo, sampleid, hashreads, hash16s, cellnum):
    with open(meta_data_out, 'w') as meta_out:  # 写模式，覆盖文件
        # 写入列头
        meta_out.write("SampleID\tName\tLibrarySize\t#ofReads\t#of16Sreads\tCellNumber\n")

        # 直接获取唯一的样品 ID
        sample_id = list(metainfo.keys())[0]

        # 写入该样品的信息
        meta_out.write(f"{metainfo[sample_id]}\t{hashreads[sampleid[sample_id]]}\t"
                       f"{hash16s[sampleid[sample_id]]:.12f}\t{cellnum[sampleid[sample_id]]:.12f}\n")

def parse_args():
    parser = argparse.ArgumentParser(description="BPtracer analysis pipeline for processing metadata.")
    parser.add_argument("--indir", help="Input directory containing sample files.")
    parser.add_argument("--outdir", help="Output directory for results.")
    parser.add_argument("--sample_id", help="Sample name.")
    parser.add_argument("--meta_data_out", help="Output metadata file.")
    parser.add_argument("--coglist", help="COG list file.")
    parser.add_argument("--config", default="../../bptracer/bptracer.config", help="Path to the configuration file (default: bptracer.config).")
    return parser.parse_args()

def main():
    args = parse_args()

    # 加载用户指定的配置模块
    config = load_config_module(args.config)

    # 生成元数据文件
    sampleid, metainfo, samplerlen = read_metadata(args.sample_id, args.meta_data_out, config.BP_META_LIBRARY_SIZE)

    # 解析 COG 列表
    seq2OGs, seqlen = parse_coglist(args.coglist)

    # 计算 Reads、16S 数和细胞数
    hashreads = {}
    hash16s = {}
    cellnum = {}

    sample = args.sample_id
    hashreads[sample] = count_reads(args.indir, sample)
    hash16s[sample] = count_16s_reads(args.indir, sample, samplerlen, config)
    cellnum[sample] = estimate_cell_number(args.indir, args.outdir, sample, seq2OGs, seqlen)

    # 更新元数据文件
    update_metadata(args.meta_data_out, metainfo, sampleid, hashreads, hash16s, cellnum)

if __name__ == "__main__":
    main()