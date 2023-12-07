
import importlib
import subprocess
import sys
import time

def import_package(package_name):
    try:
        package = importlib.import_module(package_name)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        package = importlib.import_module(package_name)

def fixed_part():
    time.sleep(5)

def main():
    start_time = time.time()
    packages = ['numpy', 'fastapi']
    for package in packages:
        import_package(package)
    fixed_part()
    end_time = time.time()
    execution_time = end_time - start_time
    return str(execution_time)

