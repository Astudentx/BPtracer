import os
from bptracer.config import *  # noqa: F401,F403

"""
User override configuration for BP-Tracer.

Import the default settings from bptracer.config, then selectively override the
few values you want to customize. Avoid editing other defaults unless
necessary to keep compatibility with existing workflows.
"""


# =============================================================================
# Optional overrides
# =============================================================================
# Fixed BP-Tracer bin root; change this if your installation lives elsewhere.
BPTRACER_BIN = "/mnt/sdb/zhangyz/bin/BPtracer/bin"
BIN_PATH = BPTRACER_BIN

# Output root (uses current working directory by default).
OUTPUT_PATH = os.getcwd()

# Refresh derived output directories after overriding OUTPUT_PATH.
set_output_path(OUTPUT_PATH)


# =============================================================================
# Tool paths (rebased to BIN_PATH)
# =============================================================================
FASTQ_STAT_SOFTWARE = os.path.join(BIN_PATH, "BPTracer/FastqStat")
FASTQSTAT_SOFTWARE = FASTQ_STAT_SOFTWARE
FASTQ_COMBINE_SOFTWARE = os.path.join(BIN_PATH, "BPTracer/Kraken2/ProcessStat.py")

KrakenTools_REPORT2MPA_SOFTWARE = os.path.join(BIN_PATH, "Kraken2/kreport2mpa.py")

Bracken_ESTABUNDANCE_SOFTWARE = os.path.join(BIN_PATH, "Bracken/est_abundance.py")
Bracken_COMBINE_SOFTWARE = os.path.join(BIN_PATH, "Bracken/combine_bracken_outputs.py")

Kraken2_MAPPING_SOFTWARE = os.path.join(BIN_PATH, "Kraken2/kraken2")
SPAdes_MAPPING_SOFTWARE = os.path.join(BIN_PATH, "SPAdes/bin/spades.py")

BP_SAMTOOLS_SOFTWARE = os.path.join(BIN_PATH, "Samtools/samtools")
BP_DIAMOND_SOFTWARE = f"{os.path.join(BIN_PATH, 'Diamond/diamond')} blastx"
BP_BLAST_SOFTWARE = os.path.join(BIN_PATH, "Blast/blastx")
BP_MINIMAP2 = os.path.join(BIN_PATH, "Minimap2/minimap2")

BP_FQ2FA_SOFTWARE = os.path.join(BIN_PATH, "BPTracer/Fq2fa.pl")
BP_EXTREA_SOFTWARE = os.path.join(BIN_PATH, "BPTracer/extract_usearch_reads.pl")
BP_MERGEFA_SOFTWARE = os.path.join(BIN_PATH, "BPTracer/MergeFa.py")

BP_USCMG_SOFTWARE = f"{os.path.join(BIN_PATH, 'Diamond/diamond0.8.16')} blastx"
