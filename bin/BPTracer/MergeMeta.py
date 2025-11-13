import os
import subprocess
import argparse
import pandas as pd

# 查找文件的函数（该版本无法正常排序）
# 该函数使用Linux系统的find命令在指定路径下查找符合条件的文件
# 仅搜索指定路径的子目录（深度为2）中的文件
# 返回找到的文件路径列表
def find_files1(search_path, filename):
    try:
        # 调用find命令查找文件
        result = subprocess.check_output(["find", search_path, "-mindepth", "2", "-maxdepth", "2", "-type", "f", "-name", filename], text=True)
        file_paths = result.strip().split("\n")
        return file_paths
    except subprocess.CalledProcessError as e:
        print(f"查找文件时出错: {e}")
        return []

# 查找文件的函数 最终版本
# 该函数使用Linux系统的find命令在指定路径下查找符合条件的文件
# 仅搜索指定路径的子目录（深度为2）中的文件，并按照文件夹名称的ll排序
# 返回找到的文件路径列表
def find_files2(search_path, filename):
    try:
        # 获取当前路径的子目录，并按ll的排序方式排序
        subdirs = sorted(
            [os.path.join(search_path, d) for d in os.listdir(search_path) if os.path.isdir(os.path.join(search_path, d))],
            key=lambda x: os.path.basename(x)
        )
        file_paths = []
        for subdir in subdirs:
            target_file = os.path.join(subdir, filename)
            if os.path.isfile(target_file):
                file_paths.append(target_file)
        return file_paths
    except Exception as e:
        print(f"查找文件时出错: {e}")
        return []


# 合并文件的函数
# 该函数读取找到的文件，并将内容合并为一个单一的数据框
# 为合并后的数据添加统一的序号，并保存为输出文件
# 如果文件无法读取，会输出相应的错误信息
def merge_files(file_paths, output_file):
    all_dataframes = []

    for file_path in file_paths:
        try:
            # 读取每个文件为DataFrame，假设文件以制表符分隔
            df = pd.read_csv(file_path, sep="\t")
            all_dataframes.append(df)
        except Exception as e:
            print(f"无法读取文件 {file_path}: {e}")

    if all_dataframes:
        # 合并所有DataFrame
        merged_df = pd.concat(all_dataframes, ignore_index=True)
        # 添加SampleID列，编号从1开始
        merged_df["SampleID"] = range(1, len(merged_df) + 1)
        # 保存合并后的数据到输出文件f
        merged_df.to_csv(output_file, sep="\t", index=False)
        print(f"所有文件已合并并保存为 {output_file}")
    else:
        print("没有有效的文件可供合并")

if __name__ == "__main__":
    # 命令行参数解析
    # -p 指定查找文件的起始路径
    # -n 指定要查找的文件名，默认为meta_data_online.txt
    # -o 指定输出文件路径，默认为./final.meta_data_online.txt
    parser = argparse.ArgumentParser(description="合并找到的meta_data_online.txt文件")
    parser.add_argument("-p", "--path", required=True, help="查找文件的起始路径")
    parser.add_argument("-n", "--name", default="meta_data_online.txt", help="要查找的文件名")
    parser.add_argument("-o", "--output", default="./final.meta_data_online.txt",help="输出文件路径")

    args = parser.parse_args()

    # 查找文件
    file_paths = find_files2(args.path, args.name)
    # 合并文件
    merge_files(file_paths, args.output)
