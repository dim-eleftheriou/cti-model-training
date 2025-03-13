import json
import os

data_path = "C:/Users/eleftheriou/Desktop/train_data/llm_batched_data"

def read_data(data_path):
    names = []
    examples = []
    objects = []
    for folder in os.listdir(data_path):
        if not folder.startswith("batch") or folder.endswith(".zip"):
            continue
        for ex in os.listdir(os.path.join(data_path, folder)):
            names.append(ex)
            with open(os.path.join(data_path, folder, ex), mode="r", encoding="utf-8") as f:
                data = json.load(f)
            examples.append(data)
            objects.append(data["output"]["objects"])
    return names, examples, objects

def filter_object_type(objects_in_example, type):
    return [obj for obj in objects_in_example if obj["type"]==type]

keep_keys = ["id",
            "spec_version",
            "name",
            #"external_references",
            "type",
            #"object_marking_refs",
            "relationship_type",
            "source_ref",
            "target_ref",
            "description",
            "identity_class",
            "object_refs"]
    
def filter_bundle_fields(dict_element, keep_keys):
    if dict_element["type"] == "marking-definition":
        return None
    else:
        drop_keys = set(list(dict_element.keys())).difference(set(keep_keys))
        for key in drop_keys:
            del dict_element[key]
        return dict_element

names, examples, objects = read_data(data_path)

types = [
    'identity', 
    #'marking-definition', 
    'report', 'relationship',
    'indicator', 'file', 'malware', 'attack-pattern', 'domain-name',
    'intrusion-set', 'url', 'vulnerability', 'location', 'hostname',
    'cryptocurrency-wallet', 'email-addr', 'ipv4-addr'
    ]
store_types = {}

for t in types:
    obj_of_interest = [filter_object_type(objects_in_example, t) for objects_in_example in objects]
    store_types[t]=obj_of_interest

os.mkdir(os.path.join(data_path, "lower_level_tasks"))
for t in types:
    os.mkdir(os.path.join(data_path, "lower_level_tasks", t))
    for i, bundle in enumerate(names):
        output = list(map(lambda x: filter_bundle_fields(x, keep_keys), store_types[t][i]))
        data_to_save = {"input":examples[i]["input"],
                        "output":output}
        with open(os.path.join(data_path, "lower_level_tasks", t, bundle), mode="w", encoding="utf-8") as f:
            json.dump(data_to_save, f)

os.mkdir(os.path.join(data_path, "lower_level_tasks", "complete_filter_bundle"))
for folder in os.listdir(data_path):
    if not folder.startswith("batch") or folder.endswith(".zip"):
        continue
    for ex in os.listdir(os.path.join(data_path, folder)):
        with open(os.path.join(data_path, folder, ex), mode="r", encoding="utf-8") as f:
            data = json.load(f)
        inputs = data["input"]
        filtered_objects = list(map(lambda x: filter_bundle_fields(x, keep_keys), data["output"]["objects"]))
        filtered_objects = [item for item in filtered_objects if item!=None]
        data["output"]["objects"] = filtered_objects
        with open(os.path.join(data_path, "lower_level_tasks", "complete_filter_bundle", ex), mode="w", encoding="utf-8") as f:
            json.dump(data, f)