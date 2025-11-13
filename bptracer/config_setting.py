import importlib

# 全局配置变量
CONFIG = None

def load_config(config_name):
    """
    动态加载配置模块
    :param config_name: 配置模块名 (如 'config_default' 或 'config_custom')
    :return: 加载的配置模块
    """
    global CONFIG
    try:
        print(f"尝试加载配置模块: bptracer.{config_name}")
        CONFIG = importlib.import_module(f"bptracer.{config_name}")
        print(f"成功加载配置模块: {CONFIG}")
    except ModuleNotFoundError as e:
        print(f"模块加载失败: {e}")
        raise ImportError(f"未找到配置模块: {config_name}")
    except Exception as e:
        print(f"加载模块时发生错误: {e}")
        raise
    return CONFIG

def load_config2(config_name):
    """
    动态加载配置模块
    :param config_name: 配置模块名 (如 'config_default' 或 'config_custom')
    :return: 加载的配置模块
    """
    global CONFIG
    try:
        full_path = f"bptracer.{config_name}"
        print(f"尝试加载配置模块: {full_path}")
        CONFIG = importlib.import_module(full_path)
        if CONFIG is None:
            raise ValueError(f"加载的模块 {full_path} 返回 None，检查模块是否正确定义")
        # 检查模块是否包含预期的内容
        expected_attributes = ['set_output_path']
        for attr in expected_attributes:
            if not hasattr(CONFIG, attr):
                raise AttributeError(f"加载的模块 {full_path} 缺少必要的属性或方法: {attr}")
        print(f"成功加载配置模块: {CONFIG}")
    except ModuleNotFoundError as e:
        print(f"模块加载失败: {e}")
        raise ImportError(f"未找到配置模块: {config_name}") from e
    except Exception as e:
        print(f"加载模块时发生未知错误: {e}")
        raise
    return CONFIG
