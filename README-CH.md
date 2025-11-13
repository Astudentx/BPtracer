
# BPtracer

**BPtracer** 是一个综合性的宏基因组数据分析工具，支持从原始测序数据出发，完成包括物种分类、功能基因识别、物种溯源以及水平基因转移（Horizontal Gene Transfer, HGT）分析的全流程处理。

## 🔧 核心功能

1. **基于 Reads 的物种分类学分析**  
    使用 Kraken2 实现高效的分类注释，默认提供基于 Pangenomes 的自建数据库，同时支持自定义数据库加载。  


2. **基于 Reads 的功能基因识别与溯源分析**  
    基于自建的Python3封装流程，支持识别并追踪以下主流功能基因：
    - 抗生素抗性基因（Antibiotic Resistance Genes, ARGs）
    - 可移动遗传元件（Mobile Genetic Elements, MGEs）
    - 毒力因子（Virulence Factors, VFs）
    - 金属抗性基因（Metal Resistance Genes, MRGs）
    - 抗压力基因（Stress Genes, SGs）


3. **基于 Contig 的水平基因转移分析（HGT）**  
    集成 [WAAFLE](https://github.com/biobakery/waafle) 工具，识别潜在的 HGT 事件。支持多种数据库（默认使用 Pangenomes 数据库，也兼容 WAAFLE 提供的 `chocophlan2` 数据库等）。

---

## 📦 安装方式

软件主提安装
```bash
# 克隆仓库
git clone https://github.com/Astudentx/BPtracer
cd BPtracer

# 创建并激活 Conda 环境
conda env create -f environment.yml
conda activate BPtracer
```
数据库安装
```bash
# 数据库较大，请通过百度网盘下载，安装到 `BPtracer/db/`中
# 下载链接：
# 链接: https://pan.baidu.com/s/xxxxxxxx 提取码: xxxx
```

---

## 🚀 快速开始

### 1. 准备工作

- 准备双端 Reads 的 FASTQ 文件；
- 创建一个 `<Paired_fastaq_list>` 文件，使用 Tab 分隔，例如：
```bash
A1	/FilePath/A1.clean.1.fq.gz	/FilePath/A1.clean.2.fq.gz
A2	/FilePath/A2.clean.1.fq.gz	/FilePath/A2.clean.2.fq.gz
A3	/FilePath/A3.clean.1.fq.gz	/FilePath/A3.clean.2.fq.gz
```

- 若进行 HGT 分析，还需准备对应样本的组装 Contig 文件，使用 Tab 分隔，例如：
```bash
A1	/FilePath/A1.contig.ok.fa
A2	/FilePath/A2.contig.ok.fa
A3	/FilePath/A3.contig.ok.fa
```


### 2. 物种分类分析以及功能基因识别与溯源分析

#### 基因注释主流程 (BP)

```bash
BPtracer BP --file <Paired_fastaq_list> --pwd <output_folder> --GeneType ARGs,MGEs
```

#### 基因序列提取与溯源表获取 (BP2)

```bash
BPtracer BP2 --file <Paired_fastaq_list> --pwd <output_folder> --GeneType ARGs
```

您同样可以使用非自带Kraken2额外的数据库分析（Kraken2）
```bash
# 默认使用 BPtracer BP 就可以在shell文件夹中生成物种分析脚本，如果您想指定数据库也可使用封装的Kraken其他数据库
BPtracer Kraken2 --file <Paired_fastaq_list> --db <database_name> --pwd <output_folder>
```

- 支持的数据库包括：`BPTax_V1`, `BPTax_V2`, `krakenDB-202212`, `krakenDB-202406`

### 3. 水平基因转移分析 (HGT)

####  Contig组装（Megahit 或 SPAdes）

```bash
# 您可以选择自己已经组装好的Contig文件
# 额外封装了Megahit与SPAdes两种主流组装软件，可基于自身情况进行挑选
# Megahit: 推荐，占用资源更少，速度更快
# SPAdes: 长度更长，识别HGT的准确性更高，识别事件更多
BPtracer Megahit --file <Paired_fastaq_list> --pwd <output_folder> # Megahit
BPtracer SPAdes   --file <Paired_fastaq_list> --pwd <output_folder> # SPAdes
```
#### 水平基因转移分析
```bash
BPtracer HGT --file <Contig_fasta_list> --db RefseqPan2 --pwd <output_folder>
```

- 可选数据库包括：`RefseqPan2`, `chocophlan2`, `UnigeneSet-waafledb.v1.fa`, `UnigeneSet-waafledb.v2.fa`

---

## 📂 Shell脚本说明与投递建议

在使用 `BPtracer` 进行数据分析时，会自动生成大量 `.sh` 脚本用于提交任务。这些脚本主要位于 `shell/` 文件夹中，结构如下所示（仅展示部分）：

```bash
# Tax分析----------------------
# Kraken2物种注释
Tax.S01.Kraken2.A1.sh
# 合并生成丰度表
Tax.S02.Kraken2.Merge.sh

# BP1分析----------------------
# BP1Reads序列统计
BP.S01.RawStat.A1.sh
# BP1Reads功能基因注释
BP.S02.ARGsAnno.A1.sh
BP.S02.MGEsAnno.A1.sh
BP.S02.MRGsAnno.A1.sh
BP.S02.SGsAnno.A1.sh
BP.S02.VFsAnno.A1.sh

# BP2分析----------------------
# BP2提取初步注释的序列进行二次注释
BP.S03.temp.ARGs.0.sh
BP.S03.temp.ARGs.1.sh
BP.S03.temp.ARGs.2.sh
BP.S03.temp.MGEs.0.sh
# BP2合并生成丰度表
BP.S04.ARGs.Merge.sh
BP.S04.MGEs.Merge.sh
BP.S04.MRGs.Merge.sh
BP.S04.SGs.Merge.sh
BP.S04.VFs.Merge.sh

# HGT分析----------------------
# Reads组装
Megahit.S01.Assambly.A1.sh
SPAdes.S01.Assambly.A1.sh
# WAAFLE分析HGT
HGT.S01.chocophlan2.A1.sh

```

### 🧭 shell脚本说明

- `Tax.`：分类学注释（Kraken2分析）
- `BP.`：基因注释与溯源（包含 ARGs, MGEs, MRGs, SGs, VFs 等）
- `Megahit.` / `SPAdes.`：基于Megahit或SPAdes的组装模块
- `HGT.`：基于WAAFLE的水平基因转移分析模块

### 🗂️ 投递规则建议

1. **不同模块可独立投递**  
   如：`BP.` 与 `Tax.` 模块可以分别提交，不必等待对方完成。

2. **同一模块需遵循流程顺序**  
   - 例如，`BP.` 模块必须按照 `BP.S01.` → `BP.S02.` → `BP.S03.` → `BP.S04.` 的顺序依次提交。
   - 每一阶段内部的不同样本脚本（如 `BP.S01.RawStat.A1.sh` ~ `A6.sh`）可并行提交。

3. **子任务自动命名**  
   - 脚本以样本编号（如 `A1` ~ `A6`）或任务编号自动命名，便于追踪分析流程。

4. **合并步骤不可跳过**  
   - 所有 `.Merge.sh` 脚本（如 `BP.S04.ARGs.Merge.sh`）需在对应阶段所有样本分析完成后再执行。

## 🧬 主要项目结构说明

```
BPtracer/
├── BPtracer/
│   ├── Kraken2.py     # 物种分类模块
│   ├── BP.py               # 主功能基因注释流程
│   ├── BP2.py             # 功能基因序列提取
│   ├── HGT.py             # WAAFLE调用脚本
│   ├── Megahit.py         # Megahit拼接
│   ├── SPAdes.py          # SPAdes拼接
│   ├── config/            # 配置模块
│   ├── tool/              # 公共函数
│   └── ...
├── bin/
│   └── BPtracer           # 主执行脚本
├── README.md
├── environment.yml        # Conda依赖环境
└── ...
```


## 🧬 主要项目结果说明

```bash
# 功能基因比对结果------------------------------------------------------------
Final.ARGs.m8.list                 # 记录每个样品的m8文件路径列表
Final.ARGs.blast.m8                # 合并所有样品中ARGs的BLAST比对结果原始文件
Final.ARGs.blast.m8.fil            # 根据Identity、Coverage等阈值过滤后的比对结果
Final.extracted.fa                 # 从所有样品中提取比对到ARGs数据库的序列
Final.extracted.fa.fil             # 基于Final.ARGs.blast.m8.fil提取序列中符合阈值要求的序列
Final.meta_data_online.txt         # 每个样品基础统计信息，包括原始reads数、16s数和cellNumber数
# 功能基因注释结果统计------------------------------------------------------------
sample_hits_count.txt              # 每个样品中匹配到的ARG基因数（未标准化）
sample_hits_rate.txt               # 每个样品中匹配到的ARG基因频率（以ppm方式标准化）

# 功能基因Type以及Subtype丰度表------------------------------------------------------------
OUT.ARGs.16s.txt                   # 所有ARG的总丰度（16S标准化），逐样品汇总
OUT.ARGs.16s.Subtype.txt           # 各Subtype的ARG丰度（以16S拷贝数为标准进行标准化）
OUT.ARGs.16s.Type.txt              # 各Type的ARG丰度（以16S拷贝数为标准进行标准化）
OUT.ARGs.cell_number.txt           # 所有ARG的总丰度（细胞数标准化），逐样品汇总
OUT.ARGs.cell_number.Subtype.txt   # 各Subtype的ARG丰度（以细胞数为标准进行标准化）
OUT.ARGs.cell_number.Type.txt      # 各Type的ARG丰度（以细胞数为标准进行标准化）
OUT.ARGs.ppm.txt                   # 所有ARG的总丰度（ppm标准化），逐样品汇总
OUT.ARGs.ppm.Subtype.txt           # 各Subtype的ARG丰度（以百万reads为标准进行标准化，ppm）
OUT.ARGs.ppm.Type.txt              # 各Type的ARG丰度（ppm标准化）

# 功能基因物种溯源分析表------------------------------------------------------------
Tax.ARGs.ppm.txt                   # 所有ARG的物种溯源信息（ppm标准化），包含全部等级
Tax.ARGs.Kingdom.ppm.txt           # ARG基因按Kingdom分类的溯源结果（ppm标准化）
Tax.ARGs.Phylum.ppm.txt            # ARG基因按Phylum分类的溯源结果（ppm标准化）
Tax.ARGs.Order.ppm.txt             # ARG基因按Order分类的溯源结果（ppm标准化）
Tax.ARGs.Class.ppm.txt             # ARG基因按Class分类的溯源结果（ppm标准化）
Tax.ARGs.Family.ppm.txt            # ARG基因按Family分类的溯源结果（ppm标准化）
Tax.ARGs.Genus.ppm.txt             # ARG基因按Genus分类的溯源结果（ppm标准化）
Tax.ARGs.Species.ppm.txt           # ARG基因按Species分类的溯源结果（ppm标准化）
Tax.ARGs.Lineage.ppm.txt           # ARG基因的完整分类路径（Lineage）的溯源结果（ppm标准化）

```

---

## 🔗 外部依赖

请确保已安装以下工具，或使用内置 Conda 环境进行统一管理：

- [Kraken2](https://ccb.jhu.edu/software/kraken2/)
- [MEGAHIT](https://github.com/voutcn/megahit)
- [SPAdes](https://github.com/ablab/spades)
- [WAAFLE](https://github.com/biobakery/waafle)
- BLAST+
---

## 📄 引用格式（如适用）

如您在研究中使用本工具，请引用以下文章/作者信息：
> **BP-tracer: A metagenomic pipeline for tracing the multifarious biopollutome**
> Yaozhong Zhang, Gaofei Jiang
> _XXXXX_ (2025)
> doi: [XXXXX](XXXXX)
---

## 📬 联系方式

如有问题或建议，欢迎通过 Issues 或 Email 联系我们。
yaozhongzyz@163.com & gjiang@njau.edu.cn