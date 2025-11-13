import pandas as pd
import argparse

def clean_and_generate_abundance_table(input_file, output_file, group_by):
    """
    清理输入数据并根据指定字段生成丰度表。

    Parameters:
        input_file (str): 输入的文件路径。
        output_file (str): 输出的文件路径。
        group_by (str): 用于分组的列名。
    """
    # 读取输入文件
    try:
        # 自动检测分隔符
        data = pd.read_csv(input_file, sep=None, engine='python')
    except Exception as e:
        print(f"读取文件失败: {e}")
        return

    # 检查分组字段是否存在
    if group_by not in data.columns:
        print(f"字段 {group_by} 不存在，请检查输入文件的列名。")
        return

    # 清理多值字段（如 Gene 列）
    for col in data.columns:
        if data[col].dtype == 'object':
            data[col] = data[col].astype(str).str.replace(r'\s+', ' ', regex=True)

    # 按指定字段分组并求和（仅限数值列）
    numeric_cols = data.select_dtypes(include='number').columns
    abundance_table = data.groupby(group_by)[numeric_cols].sum()

    # 保存结果到输出文件
    try:
        abundance_table.to_csv(output_file, sep='\t')
        print(f"丰度表已生成并保存到 {output_file}")
    except Exception as e:
        print(f"保存文件失败: {e}")

def main():
    # 配置命令行参数
    parser = argparse.ArgumentParser(description="根据指定字段生成丰度表")
    parser.add_argument("--input", required=True, help="输入文件路径")
    parser.add_argument("--output", required=True, help="输出文件路径")
    parser.add_argument("--group_by", required=True, help="用于分组的列名")

    # 解析参数
    args = parser.parse_args()

    # 调用函数生成丰度表
    clean_and_generate_abundance_table(args.input, args.output, args.group_by)

if __name__ == "__main__":
    main()
