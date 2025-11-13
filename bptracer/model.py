import argparse
import logging
import pandas as pd

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# 定义相关功能(table2CSV)
def main(input_file, output_file, *args):
    # 在这里添加主逻辑
    logger.info(f'Processing {input_file}...')

    # 示例：读取文件
    df = pd.read_table(input_file)
    # 保存结果
    df.to_csv(output_file)
    logger.info(f'Results saved to {output_file}.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Description of the script.')
    parser.add_argument('input_file', help='Path to the input file')
    parser.add_argument('output_file', help='Path to the output file')

    # 可选参数
    parser.add_argument('--param1', help='Description of param1', default='default_value')
    parser.add_argument('--param2', help='Description of param2', type=int, default=0)

    args = parser.parse_args()

    main(args.input_file, args.output_file, args.param1, args.param2)
