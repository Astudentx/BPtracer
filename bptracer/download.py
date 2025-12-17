import os
import sys
import tarfile
import shutil
import time
from typing import Dict, List

try:
    import requests
except ImportError as exc:  # pragma: no cover - runtime guard
    print("Error: requests is required for downloading databases.")
    raise

try:
    from tqdm import tqdm
except ImportError:  # pragma: no cover - optional dependency
    tqdm = None


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_DIR = os.path.join(BASE_DIR, "db")

# DOI 占位映射，可在未来替换为直接 tar.gz 下载地址
DATABASES: Dict[str, Dict[str, str]] = {
    "FUNC": {"doi": "10.5281/zenodo.17747851", "filename": "FUNC.tar.gz"},
    "HGT": {"doi": "10.5281/zenodo.17747852", "filename": "HGT.tar.gz"},
    "TAX": {"doi": "10.5281/zenodo.17747853", "filename": "TAX.tar.gz"},
}

DEFAULT_RETRIES = 3
CHUNK_SIZE = 1024 * 256  # 256KB


def doi_to_url(doi: str) -> str:
    """简单 DOI 到 URL 的转换，后续可直接替换为具体下载地址。"""
    return f"https://doi.org/{doi}"


def log(msg: str):
    print(msg, flush=True)


def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)


def download_with_progress(url: str, dest_path: str, desc: str) -> None:
    """下载文件并显示进度条。"""
    session = requests.Session()
    headers = {}
    for attempt in range(1, DEFAULT_RETRIES + 1):
        try:
            with session.get(url, stream=True, headers=headers, timeout=60) as resp:
                resp.raise_for_status()
                total = int(resp.headers.get("Content-Length", 0))
                # 若支持断点续传，可扩展此处逻辑
                progress = tqdm(total=total, unit='B', unit_scale=True, desc=desc) if tqdm else None

                with open(dest_path, "wb") as f:
                    downloaded = 0
                    for chunk in resp.iter_content(chunk_size=CHUNK_SIZE):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            if progress:
                                progress.update(len(chunk))
                            elif total:
                                percent = downloaded * 100 / total
                                sys.stdout.write(f"\r{desc}: {percent:.1f}% ({downloaded}/{total} bytes)")
                                sys.stdout.flush()
                    if progress:
                        progress.close()
                    else:
                        sys.stdout.write("\n")
                return
        except Exception as e:
            if attempt >= DEFAULT_RETRIES:
                raise
            wait = 2 ** attempt
            log(f"{desc}: download failed (attempt {attempt}/{DEFAULT_RETRIES}): {e}. Retrying in {wait}s...")
            time.sleep(wait)


def safe_extract_tar(tar_path: str, dest_dir: str):
    """安全解压，避免路径穿越。"""
    with tarfile.open(tar_path, "r:gz") as tar:
        def is_within_directory(directory, target):
            abs_directory = os.path.abspath(directory)
            abs_target = os.path.abspath(target)
            return os.path.commonpath([abs_directory]) == os.path.commonpath([abs_directory, abs_target])

        members = tar.getmembers()
        for member in members:
            target_path = os.path.join(dest_dir, member.name)
            if not is_within_directory(dest_dir, target_path):
                raise Exception(f"Unsafe path detected in tar: {member.name}")
        tar.extractall(dest_dir)


def normalize_layout(target_dir: str, module: str):
    """避免双层目录（如 target/FUNC/FUNC/*），仅在安全场景下上移一层。"""
    entries = [os.path.join(target_dir, p) for p in os.listdir(target_dir)]
    if len(entries) == 1 and os.path.isdir(entries[0]):
        inner = entries[0]
        if os.path.basename(inner).lower() == module.lower():
            log(f"[{module}] Flattening extracted directory structure.")
            for name in os.listdir(inner):
                shutil.move(os.path.join(inner, name), target_dir)
            shutil.rmtree(inner, ignore_errors=True)


def download_and_extract(module: str, url: str, filename: str):
    ensure_dir(DB_DIR)
    tmp_path = os.path.join(DB_DIR, filename)
    target_dir = os.path.join(DB_DIR, module)

    log(f"[{module}] Downloading from {url}")
    log(f"[{module}] -> {tmp_path}")
    download_with_progress(url, tmp_path, desc=f"Downloading {module}")

    # 清理目标目录，默认覆盖
    if os.path.exists(target_dir):
        log(f"[{module}] Target directory exists, removing for a clean install: {target_dir}")
        shutil.rmtree(target_dir)
    ensure_dir(target_dir)

    log(f"[{module}] Extracting to {target_dir}")
    try:
        safe_extract_tar(tmp_path, target_dir)
        normalize_layout(target_dir, module)
    except Exception as e:
        raise Exception(f"[{module}] Extraction failed: {e}")
    finally:
        try:
            os.remove(tmp_path)
        except OSError:
            pass

    log(f"[{module}] Done. Installed at {target_dir}")


def resolve_selection(args) -> List[str]:
    if not any([args.all, args.FUNC, args.HGT, args.TAX]):
        return []
    if args.all:
        return ["FUNC", "HGT", "TAX"]

    selected = []
    for key in ["FUNC", "HGT", "TAX"]:
        if getattr(args, key, False):
            selected.append(key)
    return selected


def run_download(args) -> int:
    selected = resolve_selection(args)
    if not selected:
        log("Please select at least one database: --all or --FUNC/--HGT/--TAX")
        return 1

    for module in selected:
        info = DATABASES.get(module)
        if not info:
            log(f"[{module}] Unknown module, skipped.")
            continue
        url = doi_to_url(info["doi"])
        filename = info["filename"]
        try:
            download_and_extract(module, url, filename)
        except Exception as e:
            log(f"[{module}] Failed: {e}")
            return 1
    return 0
