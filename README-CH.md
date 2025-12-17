
---
# BPtracer

**BPtracer** 是一个面向宏基因组（metagenomics）的多阶段分析流水线，可从双端测序 Reads 出发完成以下任务：

* 物种组成解析
* 功能基因识别与定量
* 功能基因宿主溯源
* 基于 Contig 的水平基因转移（Horizontal Gene Transfer, HGT）分析

BPtracer 的核心设计思想为：
**按阶段（S00–S04）生成可并行执行的 Shell 脚本，不同步骤自动串联，既适合普通服务器，又适合集群调度系统（SGE/Slurm 等）批处理。**

---

## ✨ 功能概览

### 1. Tax 模块（Tax）

基于 **Kraken2** 的物种注释，支持标准 Kraken2 数据库与 Pangenome 格式数据库（如 BPtax）。

### 2. 功能基因注释（BP / BP2）

支持以下基因类型：

* **ARGs**：抗生素抗性基因
* **MGEs**：可移动遗传元件
* **MRGs**：金属抗性基因
* **VFs**：毒力因子
* **SGs**：压力抗性基因

流程分为两部分：

* **BP**：基于 Reads 的初步功能基因注释
* **BP2**：提取目标序列 → 分块 BLAST → 合并结果 → 生成定量表与宿主溯源表

### 3. HGT 模块（HGT）

基于 **WAAFLE** 的 HGT 分析，适用于 RefseqPan2 或 chocophlan2 等数据库。

### 4. 组装模块（Megahit / SPAdes）

对 Clean Reads 进行组装，作为 HGT 分析或后续基因注释的基础。

---

## 📦 安装

```bash
# 克隆仓库
git clone https://github.com/Astudentx/BPtracer
cd BPtracer

# 环境安装
conda env create -f environment.yml
conda activate BPtracer
```

### 数据库安装

数据库较大，请通过网盘下载后解压到 `BPtracer/db/`：

```bash
链接: https://pan.baidu.com/s/xxxxxxxx   提取码: xxxx

cd BPtracer
tar -zxvf db.tar.gz
```

---

## 📥 输入文件格式

### 1. Reads 列表
SampleID  (tab) Read1_path  (tab) Read2_path 必须tab分隔
```
A1         /path/A1.1.fq.gz    /path/A1.2.fq.gz
A2         /path/A2.1.fq.gz    /path/A2.2.fq.gz
```

### 2. Contig 列表（用于 HGT）
SampleID  (tab) Contig_path 必须tab分隔
```
A1          /path/A1.contig.2k.fa
A2          /path/A2.contig.2k.fa
```

---

## 🚀 自动运行模式（推荐）

BPtracer 的所有模块均支持自动化执行：

* **直接运行 Python 脚本：**

```bash
python3 BPtracer.py MODULE_NAME [options] --auto_run
```

---

## 🔧 示例：一键分析宏基因组数据

### 1. Tax（物种分类）

```bash
python3 BPtracer.py Tax \
    --file clean.fq.list \
    --pwd Analysis \
    --auto-run \
    --max-workers 3
```

---

### 2. BP（初步功能基因注释）

```bash
python3 BPtracer.py BP \
    --file clean.fq.list \
    --pwd Analysis \
    --GeneType ARGs,MGEs,MRGs,VFs,SGs \
    --auto-run \
    --max-workers 3
```

---

### 3. BP2（序列提取 + BLAST + 溯源）

```bash
python3 BPtracer.py BP2 \
    --file clean.fq.list \
    --pwd Analysis \
    --GeneType ARGs,MGEs,MRGs,VFs,SGs \
    --auto-run \
    --max-workers 10
```

---

### 4. 组装（Megahit / SPAdes）

MEGAHIT：

```bash
python3 BPtracer.py Megahit \
    --file clean.fq.list \
    --pwd data/Contigs2 \
    --auto-run \
    --max-workers 3
```

SPAdes：

```bash
python3 BPtracer.py SPAdes \
    --file clean.fq.list \
    --pwd data/Contigs_SPades \
    --auto-run \
    --max-workers 1
```

---

### 5. HGT（基于 WAAFLE）

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

## 🧱 手动模式（适合 HPC 集群）

脚本生成在 `config.SHELL_PATH`，例如：

```
Tax.S01.Kraken2.A1.sh
BP.S02.ARGsAnno.A1.sh
BP.S03.temp.ARGs.0.sh
BP.S04.ARGs.Merge.sh
```

手动运行示例：

```bash
nohup bash BP.S02.ARGsAnno.A1.sh > A1.log 2>&1 &
```

或通过 SGE/Slurm 提交：

```bash
qsub BP.S02.ARGsAnno.A1.sh
sbatch BP.S02.ARGsAnno.A1.sh
```

---

## 📘 结果说明（Output Interpretation）

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


## 📄 引用格式

如您在研究中使用本工具，请引用以下文章/作者信息：
> **BP-Tracer: A metagenomic pipeline for tracing the multifarious biopollutome**
> Yaozhong Zhang, Gaofei Jiang
> (2025)
---

## 📬 联系方式

如有问题或建议，欢迎通过 Issues 或 Email 联系我们。
yaozhongzyz@163.com & gjiang@njau.edu.cn