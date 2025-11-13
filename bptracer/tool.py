# 加载默认配置模块
import importlib

def load_config_module_bak(config_name):
    try:
        return importlib.import_module(config_name)
    except ModuleNotFoundError as e:
        print(f"Error: Could not load configuration module '{config_name}'. {e}")
        sys.exit(1)
        
import importlib
import importlib.util
import os
import sys

def load_config_module(config_name_or_path):
    """
    动态加载配置模块，支持模块名（如 bptracer.config_custom）和文件路径（如 /path/to/config.py）。
    """
    # 判断是文件路径还是模块名
    if os.path.isfile(config_name_or_path):
        # 如果是文件路径，使用 importlib.util 加载
        print(f"从文件路径加载配置模块: {config_name_or_path}")
        spec = importlib.util.spec_from_file_location("custom_config", config_name_or_path)
        if spec is None:
            raise ImportError(f"无法加载配置文件: {config_name_or_path}")
        module = importlib.util.module_from_spec(spec)
        sys.modules["custom_config"] = module
        spec.loader.exec_module(module)
        return module
    else:
        # 否则假设是模块名，使用 importlib.import_module 加载
        print(f"从模块名加载配置模块: {config_name_or_path}")
        try:
            return importlib.import_module(config_name_or_path)
        except ModuleNotFoundError as e:
            raise ImportError(f"无法加载配置模块 '{config_name_or_path}': {e}")
        