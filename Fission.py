from time import sleep
from utils import run_shell_cmd
class FissionClient:

    def list_fns(self):
        cmd = 'fission fn list'
        res = run_shell_cmd(cmd)
        try:
            output = res.stdout.split('\n')
            names = [row.split(' ')[0] for row in output[1:] if row.split(' ')[0] != '']
            return names
        except:
            return []
    
    def list_envs(self):
        cmd = 'fission env list'
        res = run_shell_cmd(cmd)
        try:
            output = res.stdout.split('\n')
            names = [row.split(' ')[0] for row in output[1:] if row.split(' ')[0] != '']
            return names
        except:
            return []
    
    def delete_fn(self,fn):
        cmd = f'fission fn delete --name {fn}'
        res = run_shell_cmd(cmd)

    def delete_env(self,env):
        cmd = f'fission env delete --name {env}'
        res = run_shell_cmd(cmd)

    def clear_fns(self):
        fns = self.list_fns()
        for fn in fns:
            self.delete_fn(fn)

    def clear_envs(self):
        envs = self.list_envs()
        for env in envs:
            self.delete_env(env)

    def clear(self):
        self.clear_fns()
        self.clear_envs()

    def make_fn(self,function_path,env,function_name = None):
        if function_name == None:
            function_name = function_path.split('.')[0]
            function_name = f'{function_name}-{env}'

        cmd = f"fission fn create --name {function_name} --env {env} --code {function_path}"
        run_shell_cmd(cmd)
        return function_name
        

    def make_env(self,image_name,pool_size = 3, env_name = None):
        if env_name == None:
            env_name = image_name.split('/')[1].split(':')[0]

        cmd = f"docker pull {image_name}"
        run_shell_cmd(cmd)
        cmd = f"fission environment create --name {env_name} --image {image_name} --poolsize {pool_size}"
        run_shell_cmd(cmd)
        return env_name
    
    def test_fn(self,function_name):
        cmd = f"fission function test --name {function_name}"
        res = run_shell_cmd(cmd,nowait = True)

    def list_pods(self,function_name):
        cmd = f"fission fn pods --name {function_name}"
        res = run_shell_cmd(cmd)
        output = res.stdout.split('\n')
        names = [row.split(' ')[0] for row in output[1:] if row.split(' ')[0] != '']
        return names
    
    def get_fn_logs(self, function_name, pod_name):
        cmd = f"fission fn logs  --name {function_name} --pod {pod_name}"
        res = run_shell_cmd(cmd)
        output = res.stdout.split('\n')
        output = [op for op in output if op !='']
        return output
    
    def get_pod_state(self,function_name,pod_name):
        logs = self.get_fn_logs(function_name,pod_name)
        for entry in logs[::-1]:
            try:
                k,*_, = entry.split(':')
                if k == 'finished':
                    return 'warm'
                elif k == 'started':
                    return 'hot'
            except:
                continue
        return None
    
    def get_from_fn_logs(self,function_name,pod_name,key):
        logs = self.get_fn_logs(function_name,pod_name)
        for entry in logs[::-1]:
            try:
                k,*v = entry.split(':')
                if k == key:
                    return ':'.join(v).strip()
            except:
                continue
        return None
if __name__ == '__main__':
    fission = FissionClient()
    fission.list_envs()
    fission.clear()
    env = fission.make_env('red2pac/python-numpy',2,'python-numpy')
    fn =fission.make_fn('pn.py',env)
    for _ in range(3):
        fission.test_fn('pn-python-numpy')
    sleep(5)
    pods = fission.list_pods('pn-python-numpy')
    print("pods:", pods)
    # sleep(10)
    for pod in pods:
        log = fission.get_pod_state('pn-python-numpy', pod)
        print(log)
