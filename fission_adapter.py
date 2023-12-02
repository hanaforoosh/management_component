# Submit Functions
import sys

sys.path.append("../granularity_tree_component/")
from fgt import *

class Scheduler:
    def __init__(self) -> None:
        self.functions_data = dict()
        self.functions_language_and_packages = dict()
        self.freqs = dict()
        self.fgt = TreeNode('Alpine')
        self.number_of_executions = 0
        self.reconfig_threshold = 100

    def increase_execution_number(self):
        self.number_of_executions += 1
        if self.number_of_executions >= self.reconfig_threshold:
            self.fgt.reconfig()
            self.number_of_executions = 0

    def get_powerset(self,in_list):
        subsets = chain.from_iterable(
            combinations(in_list, r) for r in range(len(in_list) + 1)
        )
        powerset = [set(subset) for subset in subsets]
        return powerset

    def run_shell_cmd(self,cmd: str):
        pass
        # print(cmd)


    def make_image_name(self,language: str = None, packages: frozenset = None) -> str:
        if language == None:
            return "red2pac/alpine:latest"
        elif packages in [None, frozenset({}), frozenset()]:
            return f"red2pac/{language}:latest"

        packages = list(packages)
        image_name = f"red2pac/{language}-" + "-".join(packages) + ":latest"
        return image_name
    
    def submit_function_language_and_packages(self,name: str, language: str, packages: frozenset):
        self.functions_language_and_packages[name] = (language, packages)
        pass

    def get_language(self,name:str):
        return self.functions_language_and_packages[name][0]
        pass
    def get_packages(self,name:str):
        return self.functions_language_and_packages[name][1]
        pass



    def submit_function(self,name: str, language: str, packages: frozenset):
        self.update_frequency(packages)
        self.submit_function_language_and_packages(name, language, packages)

        ps = self.get_powerset(packages)
        for p in ps:
            fp = frozenset(p)
            image_name = self.make_image_name(language, fp)
            self.run_fission_cmd(name, image_name)
            frozen_language = frozenset({language})
            if frozen_language not in self.functions_data:
                self.functions_data[frozen_language] = [fp]
            else:
                self.functions_data[frozen_language] += [fp]
        alpine_image_name = self.make_image_name()
        self.run_fission_cmd(name, alpine_image_name)


    def update_frequency(self,packages: frozenset):
        add_value = 1
        for k in self.freqs:
            if k < packages:
                self.freqs[k] += 1
            elif packages < k:
                add_value+=1

        if packages in self.freqs:
            self.freqs[packages] += 1
        else:
            self.freqs[packages] = add_value


    def run_fission_cmd(self,function_name:str, image_name:str):
        env = image_name.replace("red2pac/", "").replace(":latest", "")
        cmd = f"docker pull {image_name}"
        self.run_shell_cmd(cmd)
        cmd = f"fission environment create --name {env} --image {image_name}"
        self.run_shell_cmd(cmd)
        cmd = f"fission fn create --name {function_name}-{env} --env {env} --code {function_name}.py"
        self.run_shell_cmd(cmd)

    def prune(self,teta:int):
        new_functions_data = dict()
        for k in self.functions_data.keys():
            new_functions_data[k] = list()
            k_set = set()
            for v in self.functions_data[k]:
                try:
                    if self.freqs[v] >= teta:
                        k_set.add(v)
                except:
                    continue

            new_functions_data[k] = list(k_set)

        self.functions_data = new_functions_data

    def print_freqs(self):
        for k,v in self.freqs.items():
            print(k,v)

    def end_submission(self,prune_teta:int):
        self.prune(prune_teta)
        self.fgt = make_tree(self.functions_data)

if __name__ == "__main__":
    scheduler = Scheduler()
    scheduler.submit_function("shadi", "python", frozenset({"a"}))
    scheduler.submit_function("shadi", "python", frozenset({"a", "b"}))
    scheduler.submit_function("shadi", "python", frozenset({"a", "b","c"}))
    lang = scheduler.get_language('shadi')
    print(lang)
    pkgs =scheduler.get_packages('shadi')
    print(pkgs)
    scheduler.end_submission(1)
    # scheduler.fgt.print_tree()
