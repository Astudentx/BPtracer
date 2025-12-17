from Bio import SeqIO
import pandas as pd
import argparse
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed

def count_reads_with_seqio(file_path):
    """
    Count the number of reads in a FASTQ or FASTQ.GZ file using Biopython's SeqIO.
    
    Parameters:
    file_path (str): Path to the FASTQ or FASTQ.GZ file.
    
    Returns:
    int: Total number of reads in the file.
    """
    return sum(1 for _ in SeqIO.parse(file_path, "fastq"))

def process_sample(sample_id, file1, file2):
    """
    Process a single sample, calculate Total_Reads_Pair and Total_Reads.
    
    Parameters:
    sample_id (str): Sample ID.
    file1 (str): Path to the first FASTQ file.
    file2 (str): Path to the second FASTQ file.
    
    Returns:
    dict: Dictionary with SampleID, Total_Reads_Pair, and Total_Reads.
    """
    # Count reads for each file
    reads_1 = count_reads_with_seqio(file1)
    reads_2 = count_reads_with_seqio(file2)
    
    # Validate pair-end matching
    if reads_1 != reads_2:
        raise ValueError(f"Mismatch in read counts for {sample_id}: {reads_1} != {reads_2}")
    
    # Calculate Total_Reads_Pair and Total_Reads
    total_reads_pair = reads_1  # Same as reads_2
    total_reads = total_reads_pair * 2
    
    return {
        "SampleID": sample_id,
        "Total_Reads_Pair": total_reads_pair,
        "Total_Reads": total_reads
    }

def process_fq_list(fq_list_path, output_path, num_threads):
    """
    Process an fq.list file using multithreading and calculate Total_Reads_Pair and Total_Reads.
    
    Parameters:
    fq_list_path (str): Path to the fq.list file containing SampleID and paired FASTQ file paths.
    output_path (str): Path to save the output results as a TSV file.
    num_threads (int): Number of threads to use.
    
    Returns:
    pd.DataFrame: DataFrame with calculated Total_Reads_Pair and Total_Reads.
    """
    # Read fq.list file
    fq_data = pd.read_csv(fq_list_path, sep="\t", header=None, names=["SampleID", "File1", "File2"])
    
    results = []
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        # Submit tasks to the thread pool
        future_to_sample = {
            executor.submit(process_sample, row["SampleID"], row["File1"], row["File2"]): row["SampleID"]
            for _, row in fq_data.iterrows()
        }
        
        # Use tqdm to monitor progress
        for future in tqdm(as_completed(future_to_sample), total=len(future_to_sample), desc="Processing Samples"):
            try:
                results.append(future.result())
            except Exception as e:
                sample_id = future_to_sample[future]
                print(f"Error processing {sample_id}: {e}")
    
    # Convert results to DataFrame
    result_df = pd.DataFrame(results)
    
    # Save results to file
    result_df.to_csv(output_path, sep="\t", index=False)
    
    return result_df

def main():
    # Define command-line arguments
    parser = argparse.ArgumentParser(description="Calculate Total_Reads_Pair and Total_Reads from an fq.list file using Biopython.")
    parser.add_argument("--file", required=True, help="Path to the fq.list file.")
    parser.add_argument("--output", required=True, help="Path to save the output results as a TSV file.")
    parser.add_argument("--threads", type=int, default=4, help="Number of threads to use (default: 4).")
    
    args = parser.parse_args()
    
    # Process fq.list and calculate results
    fq_list_path = args.file
    output_path = args.output
    num_threads = args.threads
    
    print(f"Using {num_threads} threads for processing.")
    result_df = process_fq_list(fq_list_path, output_path, num_threads)
    
    print(f"Results saved to {output_path}")
    print(result_df)

if __name__ == "__main__":
    main()
