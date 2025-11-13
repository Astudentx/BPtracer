import os
import sys
import logging
import errno
import shutil

"""Head"""
def generate_header_bptracer():
    header = (
        "    __  ___     __        ______              \n"
        "   /  |/  /__  / /_____ _/ ____/__  ____  ___ \n"
        "  / /|_/ / _ \\/ __/ __ `/ / __/ _ \\/ __ \\/ _ \\\n"
        " / /  / /  __/ /_/ /_/ / /_/ /  __/ / / /  __/\n"
        "/_/  /_/\\___/\\__/\\__,_/\\____/\\___/_/ /_/\\___/ \n"
        "                                              "
    )
    return header


def generate_header_bptracer2():
    print("██████╗ ██████╗ ████████╗██████╗  █████╗  ██████╗███████╗██████╗ ")
    print("██╔══██╗██╔══██╗╚══██╔══╝██╔══██╗██╔══██╗██╔════╝██╔════╝██╔══██╗")
    print("██████╔╝██████╔╝   ██║   ██████╔╝███████║██║     █████╗  ██████╔╝")
    print("██╔══██╗██╔═══╝    ██║   ██╔══██╗██╔══██║██║     ██╔══╝  ██╔══██╗")
    print("██████╔╝██║        ██║   ██║  ██║██║  ██║╚██████╗███████╗██║  ██║")
    print("╚═════╝ ╚═╝        ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚══════╝╚═╝  ╚═╝")




# 示例调用
if __name__ == "__main__":
    print(generate_header_bptracer())


def mkdir(path):
    """Create New directory if it does not exist."""
    folder = os.path.exists(path)
    if not folder:  # 判断是否存在文件夹如果不存在则创建为文件夹
        os.makedirs(path)  # 创建文件时如果路径不存在会创建这个路径
        print(f"***  {path}  *** ")
        print(f"***  folder has been created.  ***")
    else:
        print(f"***  {path}  *** ")
        print(f"***  folder already has been created.  ***")

def make_sure_path_exists(path):
    """Create directory if it does not exist."""
    if not path:
        return
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            logging.error('Specified path does not exist: ' + path + '\n')
            sys.exit(1)

def check_empty_dir(input_dir, overwrite=False):
    """Check the the specified directory is empty and create it if necessary."""
    if not os.path.exists(input_dir):
        make_sure_path_exists(input_dir)
    else:
        # check if directory is empty
        files = os.listdir(input_dir)
        if len(files) != 0:
            if overwrite:
                for root, dirs, files in os.walk(input_dir):
                    for f in files:
                        os.unlink(os.path.join(root, f))
                    for d in dirs:
                        shutil.rmtree(os.path.join(root, d))
            else:
                logging.error('Output directory must be empty: ' + input_dir + ' Use --force if you wish to overwrite '
                                                                               'existing directory. \n')
                sys.exit(1)



