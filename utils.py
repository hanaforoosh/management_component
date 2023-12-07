import subprocess
def run_shell_cmd(cmd: str,nowait = False):
    print('<<CMD>> ',cmd)
    if nowait:
        subprocess.Popen(cmd,shell= True)
        res = ''
    else:
        res = subprocess.run(cmd, shell=True,stdout=subprocess.PIPE,text=True)
    # res = ''
    return res