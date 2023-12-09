# Submit Functions
import sys
import subprocess
sys.path.append("../granularity_tree_component/")
from Fission import FissionClient
from fgt import *

class Scheduler:
    def __init__(self) -> None:
        self.functions_data = dict()
        self.functions_language_and_packages = dict()
        self.freqs = dict()
        self.fgt = TreeNode('Alpine')
        self.number_of_executions = 0
        self.reconfig_threshold = 100
        self.fission = FissionClient()

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


    def make_image_name(self,language: str = None, packages: frozenset = None) -> str:
        if language == None:
            return "red2pac/alpine:latest"
        elif packages in [None, frozenset({}), frozenset()]:
            return f"red2pac/{language}:latest"

        packages = sorted(list(packages))
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

    def get_function_name(self, function_path: str, language: str, packages: frozenset) -> str:
        function_name = function_path.split('.')[0]
        if packages:
            sorted_packages = sorted(packages)
            fn = f"{function_name}-{language}-{'-'.join(sorted_packages)}"
        else:
            fn = f"{function_name}-{language}"
        return fn


    def submit_function(self,function_path: str, language: str, packages: frozenset):
        self.update_frequency(packages)
        self.submit_function_language_and_packages(function_path, language, packages)

        ps = self.get_powerset(packages)
        for p in ps:
            fp = frozenset(p)
            image_name = self.make_image_name(language, fp)
            self.prepare_env_and_fn(function_path, image_name)
            frozen_language = frozenset({language})
            if frozen_language not in self.functions_data:
                self.functions_data[frozen_language] = [fp]
            else:
                self.functions_data[frozen_language] += [fp]
        alpine_image_name = self.make_image_name()
        self.prepare_env_and_fn(function_path, alpine_image_name)


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


    def prepare_env_and_fn(self,function_path:str, image_name:str):
        env = self.fission.make_env(image_name)
        self.fission.make_fn(function_path,env)

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

    def execute_tepid_function(self, function_path: str):
        pkgs = self.get_packages(function_path)
        lng = self.get_language(function_path)
        tepids = self.fgt.get_nearest_tepid(lng, pkgs)
        selected = self.tepid_selection_strategy(tepids)
        fission_fn_name = self.get_function_name(function_path,lng,selected.name)
        self.fgt.run_on(pkgs,selected)
        self.fission.test_fn(fission_fn_name)
        self.increase_execution_number()

    def execute_function(self, function_path: str):
        execute = False
        pkgs = self.get_packages(function_path)
        lng = self.get_language(function_path)
        power_set = self.get_powerset(pkgs)
        for packege in power_set:
            fission_fn_name = self.get_function_name(function_path,lng,packege)
            print("packege:", packege, "fission_fn_name:", fission_fn_name)

            pods = self.fission.list_pods(fission_fn_name)
            for pod in pods:
                log = self.fission.get_pod_state(fission_fn_name, pod)
                print("log:", log)
                if log == 'warm':
                    self.fission.test_fn(fission_fn_name)
                    execute = True 
                    break;
            if execute:
                break
        if ~execute:
            self.execute_tepid_function(function_path)
        return None

    def tepid_selection_strategy(self, tepids):
        selected = tepids[0]
        print(selected)
        return selected

if __name__ == "__main__":
    scheduler = Scheduler()
    scheduler.fission.clear()
    scheduler.submit_function("pn.py", "python", frozenset({"numpy"}))
    print(scheduler.get_packages("pn.py"))
    scheduler.submit_function("pnf.py", "python", frozenset({"fastapi", "numpy"}))
    scheduler.end_submission(1)
    scheduler.fgt.print_tree()
    scheduler.fgt.init(
        [
            frozenset({"numpy"}),
        ]
    )
    scheduler.execute_tepid_function("pnf.py")
    scheduler.execute_function("pn.py")
