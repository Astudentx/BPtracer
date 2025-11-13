import pandas as pd

# 定义接口函数
def process_stat_file(input_file, output_file):
    # 读取 Excel 文件
    df = pd.read_csv(input_file, sep='\t', dtype=str)
    # 清理列名（去除多余空格等）
    df.columns = df.columns.str.strip()
    
    # 检查是否包含必要的列
    required_columns = ["#Sample_ID", "Total_Reads", "Total_Bases", "Total_Reads_with_Ns"]
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f"输入文件缺少必要列: {', '.join(missing_columns)}")
    
    # 筛选所需列并计算 ReadsPair
    df["Total_Reads"] = pd.to_numeric(df["Total_Reads"], errors='coerce', downcast='integer')
    df["Total_Bases"] = pd.to_numeric(df["Total_Bases"], errors='coerce', downcast='integer')
    df["Total_Reads_with_Ns"] = pd.to_numeric(df["Total_Reads_with_Ns"], errors='coerce', downcast='integer')
    df["ReadsPair"] = (df["Total_Reads"] // 2).astype(int)  # 整数计算并转换为整数格式

    # 生成输出表格
    output_df = df[["#Sample_ID", "Total_Reads", "Total_Bases", "ReadsPair", "Total_Reads_with_Ns"]]
    
    # 保存新表格为 Excel 文件
    output_df.to_csv(output_file, sep='\t', index=False)
    print(f"新表格已保存到: {output_file}")

# 示例调用
input_file = "stat.main.xls"  # 输入文件路径
output_file = "stat.main.sample.xls"  # 输出文件路径
process_stat_file(input_file, output_file)
