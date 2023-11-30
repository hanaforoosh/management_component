# Submit Functions
import sys
sys.path.append('../granularity_tree_component/')
from fgt import *

def get_powerset(in_list):
    subsets = chain.from_iterable(
        combinations(in_list, r) for r in range(len(in_list) + 1)
    )
    powerset = [set(subset) for subset in subsets]
    return powerset

def make_image_name(language:str = None, packages: frozenset = None) -> str:
    if language == None:
        return 'red2pac/alpine:latest'
    elif packages in [None, frozenset({}), frozenset()]:
        return f"red2pac/{language}:latest"
    
    packages = list(packages)
    image_name = f"red2pac/{language}-" + "-".join(packages) + ":latest"
    return image_name
    
    # text = list(packages)
    # text = [t for t in text if t != "Alpine"]
    # text.sort()
    # text = "-".join(text)
    # name = f"red2pac/{language}-"
    # name += (
    #     str(text)
    #     .replace("frozenset", "")
    #     .replace("(", "")
    #     .replace(")", "")
    #     .replace("{", "")
    #     .replace("}", "")
    #     .replace("'", "")
    #     .replace('"', "")
    # )
    # name += ":latest"
    return name


def submit(name: str, language: str, packages: frozenset,nodes: dict) -> dict:
    ps = get_powerset(packages)
    for p in ps:
        fp = frozenset(p)
        image_name = make_image_name(language,fp)
        cmds = fission_cmd(name, image_name)
        print(cmds)
        frozen_language = frozenset({language})
        if frozen_language not in nodes:
            nodes[frozen_language] = [fp]
        else:
            nodes[frozen_language]+=[fp]
    
    alpine_image_name = make_image_name()
    alpine_fission_cmd = fission_cmd(name, alpine_image_name)
    print(alpine_fission_cmd)
    return nodes

def fission_cmd(name, image_name):
    env = image_name.replace("red2pac/", "").replace(":latest", "")
    fission_cmd = f"docker pull {image_name}\n"
    fission_cmd += f"fission environment create --name {env} --image {image_name}\n"
    fission_cmd += (
            f"fission fn create --name {name}-{env} --env {env} --code {name}.py\n"
        )
    
    return fission_cmd


# Execute Functions

if __name__ == "__main__":
    nodes = dict()
    submit('shadi','python',frozenset({'numpy','pandas'}),nodes)
    print(nodes)
    root = make_tree(nodes)
    root.print_tree()
