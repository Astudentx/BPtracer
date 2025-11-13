import argparse
import logging
import pandas as pd
import os

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# 定义相关功能(计算m8文件中的16s标准话丰度)
def main(input_file1, input_file2, output_file):
    logger.info(
        f'Processing {input_file1} and {input_file2}, Count Essential Single Copy Marker Genes (cell number) using diamond....')
    ## process blastx results, store subject coverage
    df1 = pd.read_csv(input_file1, sep='\t', header=None, names= names=['qseqid', 'sseqid', 'pident', 'length', 'mismatch',
                          'gapopen', 'qstart', 'qend', 'sstart', 'send',
                          'evalue', 'bitscore'])
    df2 = pd.read_csv(input_file2, sep='\t', header=None, names=['sseqid', 'ko30'])
    df = pd.merge(df1, df2,on='sseqid', how='left')
    df.to_csv()

    if len(df) == 0:
        logger.warning(f'No marker-like sequences found in file <{output_file}>.')
    else:
        if df['qseqid'].duplicated().sum() > 0:
            logger.warning('Duplicated sequences in cell number calculation.')
            df = df[~df['qseqid'].duplicated()]
            result = df.groupby('ko30').apply(lambda x: sum(x['length'] / x['slen'])).sum() / 30

            # 将结果保存到输出文件
            with open(output_file, 'w') as f:
                f.write(f'Cell number calculation result: {result}\n')
            print(result)
        # return result
    logger.info(f'Results saved to {output_file}.')




if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Description of the script.')
    parser.add_argument('input_file1', help='Path to the input file')
    parser.add_argument('input_file2', help='Path to the input file')
    parser.add_argument('output_file', help='Path to the output file')
    args = parser.parse_args()

    main(args.input_file1, args.input_file2, args.output_file)

print(os.getcwd())


input_file1="J0-1.uscmg.blastx.txt"
input_file2="ko30_structure.txt"
df1 = pd.read_csv(input_file1, sep='\t', header=None,
                  names=['qseqid', 'sseqid', 'pident', 'length', 'qlen', 'slen', 'evalue', 'bitscore', "a", "b", "c",
                         "d"])

print(df1)