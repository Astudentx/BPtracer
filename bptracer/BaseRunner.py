import os
import subprocess
from typing import List, Dict
from concurrent.futures import ThreadPoolExecutor


class BaseRunner:
    """
    BaseRunner 是一个基础运行器类，用于执行命令行任务或生成脚本文件。
    
    特点:
    - 定义了通用的命令生成和执行逻辑。
    - 使用了模板方法设计模式，要求子类实现 `build_command` 方法，以提供特定的命令生成逻辑。
    - 支持脚本生成和并行执行。

    使用场景:
    - 需要在命令行环境中执行任务时，可继承该类，实现具体的命令生成逻辑。
    """
    
    def __init__(self, **kwargs):
        """
        初始化 BaseRunner 对象。

        参数:
        - **kwargs: 任意参数字典，用于存储命令配置，例如路径、文件名等。

        属性:
        - self.params: 保存传递的参数，供子类访问。
        - self.script_path: 可选，存储生成的脚本文件路径。
        """
        self.params = kwargs
        self.script_path = None

    def build_command(self, **kwargs):
        """
        抽象方法，用于生成待执行的命令。

        参数:
        - **kwargs: 动态参数，用于生成特定任务的命令。

        返回:
        - str 或 List[str]: 待执行的命令或命令列表。

        异常:
        - 未实现时抛出 NotImplementedError。
        """
        raise NotImplementedError("Subclasses should implement this method.")

    def print_command(self, should_print=False, **kwargs):
            """
            打印生成的命令或脚本内容，便于调试。

            参数:
            - should_print (bool 或 'T'): 是否打印命令，默认为 False。
            - **kwargs: 动态参数，传递给 build_command。

            返回:
            - str 或 List[str]: 生成的命令或脚本内容。

            操作:
            - 调用 build_command 方法生成命令。
            - 如果 should_print 为 True 或 'T'，将命令打印到控制台。
            """
            cmd = self.build_command(**kwargs)   # 所有任务的命令
            if should_print in [True, 'T']:
                if isinstance(cmd, list):
                    for c in cmd:
                        print(c)
                else:
                    print(cmd)
            return cmd

    def generate_script(self, script_path: str, **kwargs):
        """
        生成脚本文件，将命令写入其中。

        参数:
        - script_path (str): 脚本文件的保存路径。
        - **kwargs: 动态参数，传递给 build_command。
        """
        self.script_path = script_path
        cmd = self.build_command(**kwargs)

        with open(script_path, "w", encoding="utf-8") as script_file:
            if isinstance(cmd, list):
                script_file.write("\n".join(cmd) + "\n")
            else:
                script_file.write(cmd + "\n")
        print(f"Script written to: {script_path}")

    def run_command(self, **kwargs):
        """
        执行生成的脚本文件或命令。

        参数:
        - **kwargs: 动态参数，传递给 build_command。
        """
        if self.script_path:  # 执行脚本文件
            if not os.path.exists(self.script_path):
                raise FileNotFoundError(f"Script file not found: {self.script_path}")
            print(f"Executing script: {self.script_path}")
            subprocess.run(f"bash {self.script_path}", shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        else:  # 直接执行命令
            cmd = self.build_command(**kwargs)
            if isinstance(cmd, list):
                for c in cmd:
                    self._run_single_command(c)
            else:
                self._run_single_command(cmd)

    def _run_single_command(self, cmd: str):
        """
        执行单条命令并处理其输出。

        参数:
        - cmd (str): 待执行的命令。
        """
        if not cmd:
            raise ValueError("build_command did not return a valid command!")
        result = subprocess.run(cmd, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0:
            print(f"Command executed successfully: {cmd}")
        else:
            print(f"Command execution failed: {cmd}")
            print(f"Standard Output: {result.stdout}")
            print(f"Standard Error: {result.stderr}")

    def run_scripts_parallel_bak(self, script_paths: List[str], script_params: List[Dict], max_workers: int = 3):
        """
        并行运行已生成的脚本文件。

        参数:
        - script_paths (List[str]): 已生成的脚本路径列表。
        - script_params (List[Dict]): 每个脚本的动态参数字典。
        - max_workers (int): 最大并行线程数，默认为 3。
        """
        def _generate_and_run(script_path, params):
            try:
                self.generate_script(script_path, **params)
                print(f"Running script: {script_path}")
                command = f"bash {script_path}"
                subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                print(f"Successfully executed script: {script_path}")
            except Exception as e:
                print(f"Error executing script {script_path}: {e}")

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            executor.map(lambda args: _generate_and_run(*args), zip(script_paths, script_params))
        
    def run_scripts_parallel(self, script_paths: List[str], max_workers: int = 3):
        """
        并行运行已生成的脚本文件。

        参数:
        - script_paths (List[str]): 已生成的脚本路径列表。
        - max_workers (int): 最大并行线程数，默认为 3。
        """
        def _run_script(script_path):
            try:
                print(f"Running script: {script_path}")
                command = f"bash {script_path}"
                result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                if result.returncode == 0:
                    print(f"Successfully executed script: {script_path}")
                else:
                    print(f"Script execution failed: {script_path}")
                    print(f"Standard Output: {result.stdout}")
                    print(f"Standard Error: {result.stderr}")
            except Exception as e:
                print(f"Error executing script {script_path}: {e}")

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            executor.map(_run_script, script_paths)
