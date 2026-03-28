# BPtracer

**BPtracer** is a multi-stage metagenomic analysis pipeline designed to process paired-end sequencing reads and perform:

* Taxonomic profiling of community composition  
* Functional gene detection and quantification  
* Host tracing for functional genes  
* Contig-based horizontal gene transfer (HGT) analysis

The core design of BPtracer is:  
**generate stage-wise (S00–S04) shell scripts that can be executed in parallel, with different stages automatically chained together**. This makes BPtracer suitable both for a single server (e.g. `nohup`) and for HPC schedulers such as SGE/Slurm.

---

## ✨ Overview of Functions

### 1. Tax module (`Tax`)

Taxonomic profiling based on **Kraken2**, supporting both standard Kraken2 databases and Pangenome-style databases (such as BPtax).

### 2. Functional gene annotation (`BP` / `BP2`)

Supported gene types:

* **ARGs**: antibiotic resistance genes  
* **MGEs**: mobile genetic elements  
* **MRGs**: metal resistance genes  
* **VFs**: virulence factors  
* **SGs**: stress-related genes  

The workflow is divided into two parts:

* **BP**: initial functional gene annotation directly from reads  
* **BP2**: extract target sequences → split into chunks for BLAST → merge results → generate abundance tables and host-tracing tables  

### 3. HGT module (`HGT`)

HGT analysis based on **WAAFLE**, compatible with databases such as RefseqPan2 and chocophlan2.

### 4. Assembly modules (`Megahit` / `SPAdes`)

Assembly of clean reads to generate contigs for downstream HGT analysis or further annotation.

---

## 📦 Installation

```bash
# Clone the repository
git clone https://github.com/Astudentx/BPtracer
cd BPtracer

# Create and activate the Conda environment
conda env create -f environment.yml
conda activate BPtracer
### Database installation

Databases are large and are distributed via Baidu Netdisk. Please download and unpack them into `BPtracer/db/`:

```bash
Link: https://pan.baidu.com/s/1CWRlWUYcu1KupAEeLOQjRA?pwd=gmur  Code: gmur
cd BPtracer
tar -zxvf db.tar.gz
```

---

## 📥 Input File Formats

### 1. Reads list

Each line: `SampleID<TAB>Read1_path<TAB>Read2_path`. **Tab-separated is required.**

```text
A1    /path/A1.1.fq.gz    /path/A1.2.fq.gz
A2    /path/A2.1.fq.gz    /path/A2.2.fq.gz
```

### 2. Contig list (for HGT)

Each line: `SampleID<TAB>Contig_path`. **Tab-separated is required.**

```text
A1    /path/A1.contig.2k.fa
A2    /path/A2.contig.2k.fa
```

---

## 🚀 Auto-run mode (recommended)

All modules of BPtracer support automated execution.

* **Run the Python script directly:**

```bash
python3 BPtracer.py MODULE_NAME [options] --auto-run
```

`MODULE_NAME` can be: `Tax`, `BP`, `BP2`, `Megahit`, `SPAdes`, `HGT`.

---

## 🔧 Example: One-click metagenomic analysis

### 1. Tax (taxonomic profiling)

```bash
python3 BPtracer.py Tax \
    --file clean.fq.list \
    --pwd Analysis \
    --auto-run \
    --max-workers 3
```

---

### 2. BP (initial functional gene annotation)

```bash
python3 BPtracer.py BP \
    --file clean.fq.list \
    --pwd Analysis \
    --GeneType ARGs,MGEs,MRGs,VFs,SGs \
    --auto-run \
    --max-workers 3
```

---

### 3. BP2 (sequence extraction + BLAST + host tracing)

```bash
python3 BPtracer.py BP2 \
    --file clean.fq.list \
    --pwd Analysis \
    --GeneType ARGs,MGEs,MRGs,VFs,SGs \
    --auto-run \
    --max-workers 10
```

---

### 4. Assembly (Megahit / SPAdes)

**MEGAHIT:**

```bash
python3 BPtracer.py Megahit \
    --file clean.fq.list \
    --pwd data/Contigs2 \
    --auto-run \
    --max-workers 3
```

**SPAdes:**

```bash
python3 BPtracer.py SPAdes \
    --file clean.fq.list \
    --pwd data/Contigs_SPades \
    --auto-run \
    --max-workers 1
```

---

### 5. HGT (WAAFLE-based)

```bash
python3 BPtracer.py HGT \
    --file contig.2k.fa.list \
    --db chocophlan2 \
    --pwd Analysis \
    -c bptracer.config \
    --auto-run \
    --max-workers 3
```

---

## 🧱 Manual mode (for HPC clusters)

All scripts are generated under `config.SHELL_PATH`, for example:

```text
Tax.S01.Kraken2.A1.sh
BP.S02.ARGsAnno.A1.sh
BP.S03.temp.ARGs.0.sh
BP.S04.ARGs.Merge.sh
```

You can run them manually, e.g.:

```bash
nohup bash BP.S02.ARGsAnno.A1.sh > A1.log 2>&1 &
```

Or submit them through SGE/Slurm:

```bash
qsub BP.S02.ARGsAnno.A1.sh
sbatch BP.S02.ARGsAnno.A1.sh
```

---

## 📘 Output Interpretation

### 🧬 Main output files (functional genes & host tracing)

```bash
# Functional gene alignment results --------------------------------------------
Final.ARGs.m8.list                 # List of m8 file paths for each sample
Final.ARGs.blast.m8                # Concatenated raw BLAST results for ARGs across all samples
Final.ARGs.blast.m8.fil            # Filtered BLAST results after applying identity/coverage thresholds
Final.extracted.fa                 # All sequences that matched the ARGs database (across samples)
Final.extracted.fa.fil             # Sequences that meet the thresholds defined in Final.ARGs.blast.m8.fil
Final.meta_data_online.txt         # Per-sample basic statistics: raw reads, 16S counts, estimated cell numbers

# Functional gene annotation summary -------------------------------------------
sample_hits_count.txt              # ARG hit counts per sample (non-normalized)
sample_hits_rate.txt               # ARG hit frequencies per sample (normalized to ppm)

# Abundance tables at Type and Subtype levels ---------------------------------
OUT.ARGs.16s.txt                   # Total ARG abundance per sample (16S-normalized)
OUT.ARGs.16s.Subtype.txt           # Subtype-level ARG abundance (normalized by 16S copy number)
OUT.ARGs.16s.Type.txt              # Type-level ARG abundance (normalized by 16S copy number)
OUT.ARGs.cell_number.txt           # Total ARG abundance per sample (cell-number-normalized)
OUT.ARGs.cell_number.Subtype.txt   # Subtype-level ARG abundance (normalized by cell number)
OUT.ARGs.cell_number.Type.txt      # Type-level ARG abundance (normalized by cell number)
OUT.ARGs.ppm.txt                   # Total ARG abundance per sample (ppm-normalized)
OUT.ARGs.ppm.Subtype.txt           # Subtype-level ARG abundance (per million reads, ppm)
OUT.ARGs.ppm.Type.txt              # Type-level ARG abundance (ppm-normalized)

# Host-tracing tables for functional genes -------------------------------------
Tax.ARGs.ppm.txt                   # ARG host-tracing table at all taxonomic levels (ppm-normalized)
Tax.ARGs.Kingdom.ppm.txt           # ARG host-tracing summarized at Kingdom level (ppm)
Tax.ARGs.Phylum.ppm.txt            # ARG host-tracing summarized at Phylum level (ppm)
Tax.ARGs.Order.ppm.txt             # ARG host-tracing summarized at Order level (ppm)
Tax.ARGs.Class.ppm.txt             # ARG host-tracing summarized at Class level (ppm)
Tax.ARGs.Family.ppm.txt            # ARG host-tracing summarized at Family level (ppm)
Tax.ARGs.Genus.ppm.txt             # ARG host-tracing summarized at Genus level (ppm)
Tax.ARGs.Species.ppm.txt           # ARG host-tracing summarized at Species level (ppm)
Tax.ARGs.Lineage.ppm.txt           # ARG host-tracing with full taxonomic lineage (ppm-normalized)
```

---

## 📄 Citation

If you use this tool in your research, please cite:

> **BP-Tracer: A metagenomic pipeline for tracing the multifarious biopollutome**
> Yaozhong Zhang, Gaofei Jiang
> (2025)
---

## 📬 Contact

For questions or suggestions, please use GitHub Issues or contact us via email:

* [yaozhongzyz@163.com](mailto:yaozhongzyz@163.com)
* [gjiang@njau.edu.cn](mailto:gjiang@njau.edu.cn)

```

这个版本是逐段一一翻译你的中文 README，保留了所有信息（包括注释、文件说明、命令行参数），只是把英语表述和 Markdown 结构整理得更统一了一点。你可以中英两个 README 并存，也可以在主仓库用英文版、在 `README_zh.md` 放中文版本。
```
