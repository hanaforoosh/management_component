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
        

    def make_env(self,image_name,env_name = None):
        if env_name == None:
            env_name = image_name.split('/')[1].split(':')[0]

        cmd = f"docker pull {image_name}"
        run_shell_cmd(cmd)
        cmd = f"fission environment create --name {env_name} --image {image_name}"
        run_shell_cmd(cmd)
        return env_name
    
    def test_fn(self,function_name):
        cmd = f"fission function test --name {function_name}"
        run_shell_cmd(cmd)

if __name__ == '__main__':
    fission = FissionClient()
    fission.clear_envs()