import os
import sys

"""
Central configuration module for BP-Tracer.

This file defines default paths, executable names, and database locations used
by BP-Tracer. Importing the module provides a complete set of defaults, while
set_output_path, set_kraken2_database, and set_HGT_database let callers adjust
specific locations at runtime without changing the underlying behavior.
"""


# =============================================================================
# Core paths
# =============================================================================
# Root directory containing the main script (e.g., /path/to/BPtracer/)
MAIN_SCRIPT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
# Main entry point script
MAIN_SCRIPT = os.path.join(MAIN_SCRIPT_DIR, "BPtracer.py")
# Location of this configuration file
CONFIG_SCRIPT = os.path.abspath(__file__)
# Executables directory
BIN_PATH = os.path.join(MAIN_SCRIPT_DIR, "bin")
# Database directory
DATABASE_PATH = os.path.join(MAIN_SCRIPT_DIR, "db")


# =============================================================================
# Output paths
# =============================================================================
# Default output root: current working directory
OUTPUT_PATH = os.getcwd()

# Initialize module-level output paths with sensible defaults
SHELL_PATH = os.path.join(OUTPUT_PATH, "shell/")
SARG_OUTPUT_PATH = os.path.join(OUTPUT_PATH, "SARG/")
Kraken2_OUTPUT_PATH = os.path.join(OUTPUT_PATH, "Kraken2/")
HGT_OUTPUT_PATH = os.path.join(OUTPUT_PATH, "WAAFLE/")
SPAdes_OUTPUT_PATH = os.path.join(OUTPUT_PATH, "Assamble_SPADde")
Megahit_OUTPUT_PATH = os.path.join(OUTPUT_PATH, "Assamble_Megahit")
BP_OUTPUT_PATH = os.path.join(OUTPUT_PATH, "BPTracer")


def set_output_path(pwd=None):
    """
    Update the root directory for analysis outputs and refresh derived paths.

    Parameters
    ----------
    pwd : str or None
        User-specified output directory. If None, uses the current working
        directory.
    """
    global OUTPUT_PATH, SHELL_PATH, SARG_OUTPUT_PATH, Kraken2_OUTPUT_PATH, HGT_OUTPUT_PATH
    global SPAdes_OUTPUT_PATH, Megahit_OUTPUT_PATH, BP_OUTPUT_PATH, BP_TAX_PATH

    if pwd is not None:
        OUTPUT_PATH = os.path.abspath(pwd)
    else:
        OUTPUT_PATH = os.getcwd()

    SHELL_PATH = os.path.join(OUTPUT_PATH, "shell/")
    SARG_OUTPUT_PATH = os.path.join(OUTPUT_PATH, "SARG/")
    Kraken2_OUTPUT_PATH = os.path.join(OUTPUT_PATH, "Kraken2/")
    HGT_OUTPUT_PATH = os.path.join(OUTPUT_PATH, "WAAFLE/")
    SPAdes_OUTPUT_PATH = os.path.join(OUTPUT_PATH, "Assamble_SPADde")
    Megahit_OUTPUT_PATH = os.path.join(OUTPUT_PATH, "Assamble_Megahit")
    BP_OUTPUT_PATH = os.path.join(OUTPUT_PATH, "BPTracer")


# """Mapping software and Functional gene databases"""
# SARG_MAPPING_SOFTWARE = "diamond blastp"
# SARG_DATABASE = os.path.join(os.path.dirname(__file__), 'db/SARG.3.2.fasta')
# SARG_EVALUE = 1e-5
# SARG_MAX_TARGET_SEQS = 10
# SARG_THREADS = 8
# SARG_FORMAT = 6


# =============================================================================
# FastqStat
# =============================================================================
FASTQ_STAT_SOFTWARE = os.path.join(BIN_PATH, "BPTracer/FastqStat")
FASTQ_COMBINE_SOFTWARE = os.path.join(BIN_PATH, "BPTracer/Kraken2/ProcessStat.py")


# =============================================================================
# KrakenTools
# =============================================================================
KrakenTools_REPORT2MPA_SOFTWARE = os.path.join("kreport2mpa.py")


# =============================================================================
# Bracken
# =============================================================================
Bracken_ESTABUNDANCE_SOFTWARE = os.path.join("est_abundance.py")
Bracken_COMBINE_SOFTWARE = os.path.join("combine_bracken_outputs.py")


# =============================================================================
# Kraken2
# =============================================================================
# Default Kraken2 executable and threading
Kraken2_MAPPING_SOFTWARE = os.path.join("kraken2")
Kraken2_THREADS = 50
# Default Kraken2 database and taxonomy list
Kraken2_DATABASE = os.path.join(DATABASE_PATH, "TAX", "BPtax")
Kraken2_TAXLIST = os.path.join(Kraken2_DATABASE, "tax.list")


def set_kraken2_database(database=None):
    """
    Set the Kraken2 database to use.

    Parameters
    ----------
    database : str or None
        None: use the default database 'BPtax'
        Non-None: treated as a Kraken2 subdirectory name under db/TAX/
        (e.g., 'BPtax'), resulting in a database path of db/TAX/<name>.
    """
    global Kraken2_DATABASE, Kraken2_TAXLIST

    if database is None:
        Kraken2_DATABASE = os.path.join(DATABASE_PATH, "TAX", "BPtax")
        Kraken2_TAXLIST = os.path.join(Kraken2_DATABASE, "tax.list")
    else:
        Kraken2_DATABASE = os.path.join(DATABASE_PATH, "TAX", database)
        Kraken2_TAXLIST = os.path.join(Kraken2_DATABASE, "tax.list")


# =============================================================================
# BP-Tracer core workflow
# =============================================================================
BP_SAMTOOLS_SOFTWARE = os.path.join("samtools")
BP_DIAMOND_SOFTWARE = os.path.join("diamond blastx")
BP_BLAST_SOFTWARE = os.path.join("blastx")

BP_FQ2FA_SOFTWARE = os.path.join(BIN_PATH, "BPTracer/Fq2fa.pl")
BP_FQ2FA_SOFTWARE2 = "seqtk"  # Alternative fastq-to-fasta conversion option
BP_MINIMAP2 = os.path.join("minimap2")

BP_EXTREA_SOFTWARE = os.path.join(BIN_PATH, "BPTracer/extract_usearch_reads.pl")
BP_MERGEFA_SOFTWARE = os.path.join(BIN_PATH, "BPTracer/MergeFa.py")
BP_16S_DATABASE = os.path.join(DATABASE_PATH, "FUNC/BPfunc/gg85_yinxiaole.fasta.mmi")
BP_USCMG_DATABASE = os.path.join(DATABASE_PATH, "FUNC/BPfunc/KO30_DIAMOND.dmnd")
BP_USCMG_LIST = os.path.join(DATABASE_PATH, "FUNC/BPfunc/all_KO30_name.list")

"""BP-Tracer Old USCMG databases"""
# BP_USCMG_SOFTWARE = os.path.join(BIN_PATH,"BPTracer/diamond0.8.16 blastx")
# BP_USCMG_DATABASE = os.path.join(DATABASE_PATH, 'FUNC/BPfunc/KO30_DIAMOND.0.8.16.dmnd')
BP_USCMG_SOFTWARE = os.path.join("diamond blastx")


# =============================================================================
# BP-Tracer analysis strategy
# =============================================================================
BP2_STRATEGY = "sample"  # Accepts "sample" or "chunk"


# =============================================================================
# BP-Tracer functional gene databases
# =============================================================================
BP_EXTRACTEDFA_WINDOW = 200000
BP_META_LIBRARY_SIZE = 300
BP_TAX_DATABASE = os.path.join(DATABASE_PATH, "FUNC/BPfunc/species.Tax.txt")

# DIAMOND databases
BP_ARG_DATABASE = os.path.join(DATABASE_PATH, "FUNC/BPfunc/Gene-ARG.dmnd")
BP_MGE_DATABASE = os.path.join(DATABASE_PATH, "FUNC/BPfunc/Gene-MGE.dmnd")
BP_MRG_DATABASE = os.path.join(DATABASE_PATH, "FUNC/BPfunc/Gene-MRG.dmnd")
BP_VFs_DATABASE = os.path.join(DATABASE_PATH, "FUNC/BPfunc/Gene-VFs.dmnd")
BP_SGs_DATABASE = os.path.join(DATABASE_PATH, "FUNC/BPfunc/Gene-SGs.dmnd")
# Functional gene structure metadata
BP_ARG_STRUCTURE = os.path.join(DATABASE_PATH, "FUNC/BPfunc/Gene-ARG.list")
BP_MGE_STRUCTURE = os.path.join(DATABASE_PATH, "FUNC/BPfunc/Gene-MGE.list")
BP_MRG_STRUCTURE = os.path.join(DATABASE_PATH, "FUNC/BPfunc/Gene-MRG.list")
BP_VFs_STRUCTURE = os.path.join(DATABASE_PATH, "FUNC/BPfunc/Gene-VFs.list")
BP_SGs_STRUCTURE = os.path.join(DATABASE_PATH, "FUNC/BPfunc/Gene-SGs.list")
# BLAST amino acid libraries
BP_BLASTARG_DATABASE = os.path.join(DATABASE_PATH, "FUNC/BPfunc/Gene-ARG.faa")
BP_BLASTMGE_DATABASE = os.path.join(DATABASE_PATH, "FUNC/BPfunc/Gene-MGE.faa")
BP_BLASTMRG_DATABASE = os.path.join(DATABASE_PATH, "FUNC/BPfunc/Gene-MRG.faa")
BP_BLASTVFs_DATABASE = os.path.join(DATABASE_PATH, "FUNC/BPfunc/Gene-VFs.faa")
BP_BLASTSGs_DATABASE = os.path.join(DATABASE_PATH, "FUNC/BPfunc/Gene-SGs.faa")

# Profile thresholds
BP_LENGTH_THRESHOLD = 25
BP_IDENTITY_THRESHOLD = 80
BP_EVALUE_THRESHOLD = 1E-7


# =============================================================================
# SPAdes
# =============================================================================
SPAdes_MAPPING_SOFTWARE = os.path.join("spades.py")
SPAdes_THREADS = 140
SPAdes_MEMORY = 400


# =============================================================================
# Megahit
# =============================================================================
Megahit_MAPPING_SOFTWARE = os.path.join("megahit")
Megahit_THREADS = 40
Megahit_MIN_LENGTH = 500


# =============================================================================
# HGT (WAAFLE)
# =============================================================================
# Default HGT database: UnigeneSet-waafledb.v2.fa
FILTER_SOFTWARE = os.path.join(BIN_PATH, "BPTracer/FilterContigsByLength.py")
BP_HGT_DATABASE = os.path.join(DATABASE_PATH, "HGT/BPtrans/BPtrans")
BP_HGT_STRUCTURE = os.path.join(DATABASE_PATH, "HGT/BPtrans/BPtrans_taxonomy.tsv")


def set_HGT_database(database=None):
    """
    Set the HGT database to use.

    Parameters
    ----------
    database : str or None
        None: use the default database 'BPtrans'
        Non-None: treated as a subdirectory name under db/HGT/, resulting in
        db/HGT/<name>/<name> and db/HGT/<name>/<name>_taxonomy.tsv.
    """
    global BP_HGT_DATABASE, BP_HGT_STRUCTURE

    if database is None:
        BP_HGT_DATABASE = os.path.join(DATABASE_PATH, "HGT/BPtrans/BPtrans")
        BP_HGT_STRUCTURE = os.path.join(DATABASE_PATH, "HGT/BPtrans/BPtrans_taxonomy.tsv")
    else:
        BP_HGT_DATABASE = os.path.join(DATABASE_PATH, "HGT/", database, database)
        BP_HGT_STRUCTURE = os.path.join(DATABASE_PATH, "HGT/", database, f"{database}_taxonomy.tsv")
