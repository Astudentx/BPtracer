#!/usr/bin/env python3
"""
Quick contig-length filter for FASTA files.

Usage:
    python FilterContigsByLength.py --input contigs.fa --output filtered.fa --min-length 1000
"""

import argparse
from typing import Tuple


def filter_fasta_by_length(input_path: str, output_path: str, min_length: int) -> Tuple[int, int]:
    """
    Filter sequences shorter than min_length from a FASTA file.

    Returns (total, kept).
    """
    total, kept = 0, 0
    header = None
    seq_parts = []

    with open(input_path, "r") as fin, open(output_path, "w") as fout:
        for line in fin:
            if not line:
                continue
            if line.startswith(">"):
                if header is not None:
                    total, kept = _flush_record(header, seq_parts, min_length, fout, total, kept)
                header = line.strip()
                seq_parts = []
            else:
                seq_parts.append(line.strip())

        if header is not None:
            total, kept = _flush_record(header, seq_parts, min_length, fout, total, kept)

    return total, kept


def _flush_record(header, seq_parts, min_length, fout, total, kept):
    total += 1
    seq = "".join(seq_parts)
    if len(seq) >= min_length:
        fout.write(f"{header}\n")
        # Wrap sequence to avoid extremely long lines downstream
        for i in range(0, len(seq), 80):
            fout.write(seq[i:i + 80] + "\n")
        kept += 1
    return total, kept


def main():
    parser = argparse.ArgumentParser(description="Filter FASTA contigs by minimum length.")
    parser.add_argument("--input", "-i", required=True, help="Input FASTA file.")
    parser.add_argument("--output", "-o", required=True, help="Output FASTA file after filtering.")
    parser.add_argument(
        "--min-length",
        "-l",
        type=int,
        default=1000,
        help="Minimum contig length to keep (bp). Default: 1000.",
    )
    args = parser.parse_args()

    total, kept = filter_fasta_by_length(args.input, args.output, args.min_length)
    print(f"Total contigs: {total}; kept (>= {args.min_length} bp): {kept}")


if __name__ == "__main__":
    main()
