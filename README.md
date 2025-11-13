
# BPtracer

**BPtracer** is a comprehensive metagenomic data analysis tool that supports end-to-end processing, including species classification, functional gene identification, species tracing, and Horizontal Gene Transfer (HGT) analysis, starting from raw sequencing data.

## 🔧 Core Features

1. **Reads-based Species Classification**  
    Uses Kraken2 for efficient taxonomic annotation. The tool comes with a pre-built Pangenomes-based database and also supports custom database loading.

2. **Reads-based Functional Gene Identification and Tracing**  
    Based on a custom Python3 workflow, it supports the identification and tracing of the following major functional genes:
    - Antibiotic Resistance Genes (ARGs)
    - Mobile Genetic Elements (MGEs)
    - Virulence Factors (VFs)
    - Metal Resistance Genes (MRGs)
    - Stress Genes (SGs)

3. **Contig-based Horizontal Gene Transfer (HGT) Analysis**  
    Integrates the [WAAFLE](https://github.com/biobakery/waafle) tool for identifying potential HGT events. It supports multiple databases (default Pangenomes database, as well as WAAFLE's `chocophlan2` database, etc.).

---

## 📦 Installation

### Main Installation

```bash
# Clone the repository
git clone https://github.com/Astudentx/BPtracer
cd BPtracer

# Create and activate the Conda environment
conda env create -f environment.yml
conda activate BPtracer
```

### Database Installation

```bash
# The database is large, please download it from Baidu Netdisk and install it in the `BPtracer/db/` directory
# Download link:
# Link: https://pan.baidu.com/s/xxxxxxxx Extract code: xxxx
```

---

## 🚀 Quick Start

### 1. Preparation

- Prepare paired-end FASTQ files;
- Create a `<Paired_fastaq_list>` file using Tab delimiters, e.g.:
```bash
A1	/FilePath/A1.clean.1.fq.gz	/FilePath/A1.clean.2.fq.gz
A2	/FilePath/A2.clean.1.fq.gz	/FilePath/A2.clean.2.fq.gz
A3	/FilePath/A3.clean.1.fq.gz	/FilePath/A3.clean.2.fq.gz
```

- For HGT analysis, also prepare the corresponding assembled Contig files, using Tab delimiters, e.g.:
```bash
A1	/FilePath/A1.contig.ok.fa
A2	/FilePath/A2.contig.ok.fa
A3	/FilePath/A3.contig.ok.fa
```

### 2. Species Classification and Functional Gene Identification and Tracing

#### Gene Annotation Main Workflow (BP)

```bash
BPtracer BP --file <Paired_fastaq_list> --pwd <output_folder> --GeneType ARGs,MGEs
```

#### Gene Sequence Extraction and Tracing Table Generation (BP2)

```bash
BPtracer BP2 --file <Paired_fastaq_list> --pwd <output_folder> --GeneType ARGs
```

You can also perform analysis with external Kraken2 databases (Kraken2):
```bash
# By default, BPtracer BP will generate species analysis scripts in the shell folder. To specify a database, use Kraken's other databases.
BPtracer Kraken2 --file <Paired_fastaq_list> --db <database_name> --pwd <output_folder>
```

- Supported databases include: `BPTax_V1`, `BPTax_V2`, `krakenDB-202212`, `krakenDB-202406`

### 3. Horizontal Gene Transfer Analysis (HGT)

#### Contig Assembly (Megahit or SPAdes)

```bash
# You can choose your own assembled Contig files
# Additionally, Megahit and SPAdes assembly tools are provided for you to choose based on your needs
# Megahit: Recommended for less resource usage and faster speed
# SPAdes: Longer contigs, better accuracy, and more HGT events identified
BPtracer Megahit --file <Paired_fastaq_list> --pwd <output_folder> # Megahit
BPtracer SPAdes   --file <Paired_fastaq_list> --pwd <output_folder> # SPAdes
```

#### Horizontal Gene Transfer Analysis

```bash
BPtracer HGT --file <Contig_fasta_list> --db RefseqPan2 --pwd <output_folder>
```

- Optional databases include: `RefseqPan2`, `chocophlan2`, `UnigeneSet-waafledb.v1.fa`, `UnigeneSet-waafledb.v2.fa`

---

## 📂 Shell Script Explanation and Submission Recommendations

When using `BPtracer` for data analysis, a large number of `.sh` scripts are automatically generated for task submission. These scripts are located in the `shell/` folder, structured as follows (partial view):

```bash
# Tax Analysis----------------------
# Kraken2 species annotation
Tax.S01.Kraken2.A1.sh
# Merge to generate abundance table
Tax.S02.Kraken2.Merge.sh

# BP1 Analysis----------------------
# BP1 Reads sequence statistics
BP.S01.RawStat.A1.sh
# BP1 Reads functional gene annotation
BP.S02.ARGsAnno.A1.sh
BP.S02.MGEsAnno.A1.sh
BP.S02.MRGsAnno.A1.sh
BP.S02.SGsAnno.A1.sh
BP.S02.VFsAnno.A1.sh

# BP2 Analysis----------------------
# BP2 extract sequences for secondary annotation
BP.S03.temp.ARGs.0.sh
BP.S03.temp.ARGs.1.sh
BP.S03.temp.ARGs.2.sh
BP.S03.temp.MGEs.0.sh
# BP2 merge and generate abundance table
BP.S04.ARGs.Merge.sh
BP.S04.MGEs.Merge.sh
BP.S04.MRGs.Merge.sh
BP.S04.SGs.Merge.sh
BP.S04.VFs.Merge.sh

# HGT Analysis----------------------
# Reads assembly
Megahit.S01.Assambly.A1.sh
SPAdes.S01.Assambly.A1.sh
# WAAFLE HGT analysis
HGT.S01.chocophlan2.A1.sh

```

### 🧭 Shell Script Explanation

- `Tax.`: Taxonomic annotation (Kraken2 analysis)
- `BP.`: Functional gene annotation and tracing (including ARGs, MGEs, MRGs, SGs, VFs, etc.)
- `Megahit.` / `SPAdes.`: Assembly modules based on Megahit or SPAdes
- `HGT.`: Horizontal Gene Transfer analysis based on WAAFLE

### 🗂️ Submission Rules Recommendations

1. **Different Modules Can Be Submitted Independently**  
   E.g., `BP.` and `Tax.` modules can be submitted separately without waiting for each other to finish.

2. **Submit Tasks in Sequence Within the Same Module**  
   - For example, in the `BP.` module, submit tasks in the order of `BP.S01.` → `BP.S02.` → `BP.S03.` → `BP.S04.`
   - Different sample scripts within each stage (e.g., `BP.S01.RawStat.A1.sh` ~ `A6.sh`) can be submitted in parallel.

3. **Subtasks Are Automatically Named**  
   - Scripts are automatically named by sample ID (e.g., `A1` ~ `A6`) or task number, making it easier to track the analysis process.

4. **Do Not Skip Merge Steps**  
   - All `.Merge.sh` scripts (e.g., `BP.S04.ARGs.Merge.sh`) must be executed after all sample analyses in the corresponding stage are complete.

## 🧬 Main Project Structure

```
BPtracer/
├── BPtracer/
│   ├── Kraken2.py     # Species classification module
│   ├── BP.py               # Main functional gene annotation workflow
│   ├── BP2.py             # Functional gene sequence extraction
│   ├── HGT.py             # WAAFLE script for HGT
│   ├── Megahit.py         # Megahit assembly
│   ├── SPAdes.py          # SPAdes assembly
│   ├── config/            # Configuration module
│   ├── tool/              # Common functions
│   └── ...
├── bin/
│   └── BPtracer           # Main execution script
├── README.md
├── environment.yml        # Conda environment dependencies
└── ...
```

## 🧬 Main Project Output Description

```bash
以下是你提供的 Bash 注释内容的英文翻译：


# Functional Gene Alignment Results------------------------------------------------------------
Final.ARGs.m8.list                 # List of m8 file paths for each sample
Final.ARGs.blast.m8                # Merged raw BLAST alignment results for ARGs from all samples
Final.ARGs.blast.m8.fil            # Filtered alignment results based on Identity, Coverage, etc.
Final.extracted.fa                 # Sequences extracted from all samples that match the ARGs database
Final.extracted.fa.fil             # Sequences extracted from Final.ARGs.blast.m8.fil that meet the threshold requirements
Final.meta_data_online.txt         # Basic statistics for each sample, including raw reads, 16S count, and cell number

# Functional Gene Annotation Result Statistics------------------------------------------------------------
sample_hits_count.txt              # Number of ARGs matched in each sample (unnormalized)
sample_hits_rate.txt               # Frequency of matched ARGs in each sample (ppm normalized)

# Functional Gene Type and Subtype Abundance Tables------------------------------------------------------------
OUT.ARGs.16s.txt                   # Total abundance of all ARGs (16S normalized), summarized by sample
OUT.ARGs.16s.Subtype.txt           # Abundance of each ARG Subtype (16S copy number normalized)
OUT.ARGs.16s.Type.txt              # Abundance of each ARG Type (16S copy number normalized)
OUT.ARGs.cell_number.txt           # Total abundance of all ARGs (cell number normalized), summarized by sample
OUT.ARGs.cell_number.Subtype.txt   # Abundance of each ARG Subtype (cell number normalized)
OUT.ARGs.cell_number.Type.txt      # Abundance of each ARG Type (cell number normalized)
OUT.ARGs.ppm.txt                   # Total abundance of all ARGs (ppm normalized), summarized by sample
OUT.ARGs.ppm.Subtype.txt           # Abundance of each ARG Subtype (ppm normalized, based on million reads)
OUT.ARGs.ppm.Type.txt              # Abundance of each ARG Type (ppm normalized)

# Functional Gene Species Tracing Analysis Tables------------------------------------------------------------
Tax.ARGs.ppm.txt                   # Species tracing information for all ARGs (ppm normalized), includes all taxonomic levels
Tax.ARGs.Kingdom.ppm.txt           # Species tracing results for ARGs by Kingdom (ppm normalized)
Tax.ARGs.Phylum.ppm.txt            # Species tracing results for ARGs by Phylum (ppm normalized)
Tax.ARGs.Order.ppm.txt             # Species tracing results for ARGs by Order (ppm normalized)
Tax.ARGs.Class.ppm.txt             # Species tracing results for ARGs by Class (ppm normalized)
Tax.ARGs.Family.ppm.txt            # Species tracing results for ARGs by Family (ppm normalized)
Tax.ARGs.Genus.ppm.txt             # Species tracing results for ARGs by Genus (ppm normalized)
Tax.ARGs.Species.ppm.txt           # Species tracing results for ARGs by Species (ppm normalized)
Tax.ARGs.Lineage.ppm.txt           # Full taxonomic lineage tracing results for ARGs (ppm normalized)
```
