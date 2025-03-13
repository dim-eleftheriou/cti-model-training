import os
import ast
import json

def read_bundle(path, bundle):
    """Read a .json file by specifying the name of 
    the file (bundle) and the path that is located"""
    if not bundle.endswith(".json"):
        print(f"{bundle} is not accepted. Only .json type is accepted!")
    else:
        with open(os.path.join(path, bundle), mode="r", encoding="utf-8") as f:
            data = json.load(f)
        if not type(data["output"])==dict:
            data["output"] = ast.literal_eval(data["output"])
    return data

def save_bundle(path, bundle, data):
    """Save a .json file by specifying the name of 
    the file (bundle), the path that is located and
    data to save in a dict type."""
    if not bundle.endswith(".json"):
        print(f"{bundle} is not accepted. Only .json type is accepted!")
    else:
        with open(os.path.join(path, bundle), mode="w", encoding="utf-8") as f:
            json.dump(data, f)

def read_bundles_in_path(path):
    """Read all bundles located in a path and returns a dict with 
    keys being the names of the files and values the data reside in the file"""
    dict_of_data = dict()
    for bundle in os.listdir(path):
        dict_of_data[bundle] = read_bundle(path, bundle)
    return dict_of_data

def read_bundles_in_path_splitted(path):
    """Read all bundles located in a path and returns a list of names, 
    a list with the data reside in the file and a list with the cubersecurity
    objects report in the bundle"""
    names = []
    examples = []
    objects = []
    for bundle in os.listdir(path):
        data = read_bundle(path, bundle)
        names.append(bundle)
        examples.append(data)
        objects.append(data["output"]["objects"])
    return names, examples, objects

def filter_object_type(objects_in_example, type):
    """Filters all objects that of different type than the one specified.
    The input is a list of objects"""
    return [obj for obj in objects_in_example if obj["type"]==type]
    
def filter_bundle_fields(bundle_object, keep_keys=None):
    """Filters all keys except the ones explicitly specified to be kept.
       The input is an object of type dict."""
    obj = bundle_object.copy()
    if keep_keys:
        pass
    else:
        keep_keys = [
            "id", "spec_version", "name",
            "type", "relationship_type",
            "source_ref", "target_ref",
            "description", "identity_class",
            "object_refs", "labels"
            ]
    drop_keys = set(list(obj.keys())).difference(set(keep_keys))
    for key in drop_keys:
        del obj[key]
    return obj

def filter_lists_of_bundle_fields(list_of_bundle_objects, keep_keys=None):
    """Filters all keys except the ones explicitly specified to be kept in
    a list of objects of type dict"""
    return list(map(lambda x: (filter_bundle_fields(x, keep_keys)), list_of_bundle_objects))