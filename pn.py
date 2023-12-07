
import importlib
import subprocess
import sys
import time
from datetime import datetime
import subprocess

def import_package(package_name):
    try:
        package = importlib.import_module(package_name)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        package = importlib.import_module(package_name)

def fixed_part():
    time.sleep(5)

def main():
    res = subprocess.run('hostname', shell=True,stdout=subprocess.PIPE,text=True)
    print('podname:',res.stdout)
    print('started:',datetime.now().time())
    start_time = time.time()
    packages = ['numpy']
    for package in packages:
        import_package(package)
    fixed_part()
    end_time = time.time()
    execution_time = end_time - start_time
    print('finished:',datetime.now().time())
    return str(execution_time)

