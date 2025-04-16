import os
import ast
import json
import copy
import time

def read_bundle(path, bundle):
    """Read a .json file by specifying the name of 
    the file (bundle) and the path that is located"""
    if not bundle.endswith(".json"):
        print(f"{bundle} is not accepted. Only .json type is accepted!")
    else:
        with open(os.path.join(path, bundle), mode="r", encoding="utf-8") as f:
            data = json.load(f)
        if not type(data)==dict:
            data = ast.literal_eval(data)
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
            "object_refs", "labels", "value",
            "hashes"
            ]
    if obj["type"] == "marking-definition":
        return None
    else:
        drop_keys = set(list(obj.keys())).difference(set(keep_keys))
        for key in drop_keys:
            del obj[key]
        return obj

def filter_lists_of_bundle_fields(list_of_bundle_objects, keep_keys=None):
    """Filters all keys except the ones explicitly specified to be kept in
    a list of objects of type dict"""
    objects_list = list(map(lambda x: (filter_bundle_fields(x, keep_keys)), list_of_bundle_objects))
    cleaned_list = [obj for obj in objects_list if obj is not None]
    return cleaned_list

def replace_ids_in_bundle(bundle):
    new_bundle = copy.deepcopy(bundle)

    # First delete the bundle id
    new_bundle["id"] = ""

    # Then extract all ids that should be replaced as well as the candidate replacement
    fields = dict(
        id = list(),
        type = list(),
        name = list(),
        source_ref = list(),
        target_ref = list(),
        relationship_type = list(),
        value = list(),
        hashes = list()
    )
    for obj in new_bundle["objects"]:
        for f in fields.keys():
            if f in obj.keys():
                fields[f].append(obj[f])
            else:
                fields[f].append("")
    
    to_replace = []
    for i, _ in enumerate(fields["id"]):
        replacement = ""
        if fields["name"][i]!="":
            replacement += fields["type"][i] + "--" + fields["name"][i]
        elif fields["source_ref"][i]!="" and fields["target_ref"][i]!="":
            replacement += fields["type"][i] + "--" + fields["source_ref"][i] + "--" + fields["relationship_type"][i] + "--" + fields["target_ref"][i]
        elif fields["value"][i]!="":
            replacement += fields["type"][i] + "--" + fields["value"][i]
        elif fields["hashes"][i]!="":
            replacement += fields["type"][i] + "--" + fields["hashes"][i]["SHA-256"]
        else:
            raise Exception("No ID is created")

        replacement = replacement.replace(" ", "-")
        to_replace.append(replacement)


    for i, idd in enumerate(fields["id"]):
        for r in to_replace:
            if idd in r:
                to_replace[to_replace.index(r)] = r.replace(idd, to_replace[i])


    ids_for_replacement = {k:to_replace[i] for i, k in enumerate(fields["id"])}


    for i, obj in enumerate(new_bundle["objects"]):
        c_obj = copy.deepcopy(obj)
        c_obj["id"] = copy.deepcopy(ids_for_replacement[obj["id"]])
        if "source_ref" in obj.keys():
            c_obj["source_ref"] = copy.deepcopy(ids_for_replacement[obj["source_ref"]])
        if "target_ref" in obj.keys():
            c_obj["target_ref"] = copy.deepcopy(ids_for_replacement[obj["target_ref"]])
        if "object_refs" in obj.keys():
            object_refs = copy.deepcopy(obj["object_refs"])
            for j, ref in enumerate(obj["object_refs"]):
                object_refs[j] = copy.deepcopy(ids_for_replacement[ref])
            c_obj["object_refs"] = object_refs
        new_bundle["objects"][i] = c_obj

    return new_bundle

