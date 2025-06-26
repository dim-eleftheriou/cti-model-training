import os
import ast
import json
import copy
from typing import Union, Optional
from pydantic import ValidationError
from StixConfig import (SDO, SCO, File, StixToPydanticMap)

smap = StixToPydanticMap()

def read_bundle(path:str, bundle:str) -> dict:
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

def save_bundle(path:str, bundle:str, data:dict) -> None:
    """Save a .json file by specifying the name of 
    the file (bundle), the path that is located and
    data to save in a dict type."""
    if not bundle.endswith(".json"):
        print(f"{bundle} is not accepted. Only .json type is accepted!")
    else:
        with open(os.path.join(path, bundle), mode="w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, default=str)

def read_bundles_in_path(path: str) -> dict:
    """Read all bundles located in a path and returns a dict with 
    keys being the names of the files and values the data reside in the file"""
    dict_of_data = dict()
    for bundle in os.listdir(path):
        dict_of_data[bundle] = read_bundle(path, bundle)
    return dict_of_data

def filter_objects_from_bundle(stix_bundle: dict, ignore_objects: dict) -> dict:
    """Removes any STIX object included in the dict ignore_objects.
    Keys are object types and values are lists of specific object fields/values."""
    new_objects = []
    for obj in stix_bundle["objects"]:

        obj_type = obj["type"]

        if obj_type not in ignore_objects.keys():
            new_objects.append(obj)
        else:
            for comparison_field, comparison_value in ignore_objects[obj_type]:
                if obj[comparison_field]!=comparison_value:
                    new_objects.append(obj)
                else:
                    continue

    filtered_stix_bundle = {"type":stix_bundle["type"],
                            "id":stix_bundle["id"],
                            "objects":new_objects}
    return filtered_stix_bundle

def filter_object_fields(stix_object: dict) -> dict:
    """Filters the fields of a STIX Object according to STIXConfig."""
    filterd_stix_object = smap(stix_object).model_dump()
    final_stix_object = {k:v for k, v in filterd_stix_object.items() if v is not None}
    return final_stix_object

def filter_object_fields_from_bundle(stix_bundle: dict) -> dict:
    """Filters the fields of all STIX Objects in a STIX bundle"""
    new_objects = [filter_object_fields(obj) for obj in stix_bundle["objects"]]
    filtered_stix_bundle = {"type":stix_bundle["type"],
                            "id":stix_bundle["id"],
                            "objects":new_objects}
    return filtered_stix_bundle
    
def filter_bundles(stix_bundles: dict, config: dict) -> list:
    """Applies the function filter_object_fields to a dictionary of STIX bundles.
    Keys are the names of the bundles and values are the data."""
    ignore_objects = config["stix_objects_to_ignore"]
    # Apply field filtering and validation
    validated_stix_bundles = {}
    validation_failures = {}
    for k, v in stix_bundles.items():
        try:
            validated_stix_bundles[k] = filter_object_fields_from_bundle(v)
        except ValidationError as e:
            validation_failures[k] = e
    if validation_failures:
        message = f"""{len(validation_failures)} STIX bundles failed on Validation process.
        These are the bundles which failed: {validation_failures}"""
    else:
        message = ""
        
    if ignore_objects:
        # Apply object filtering
        filtered_stix_bundles = {k:filter_objects_from_bundle(v, ignore_objects) for k, v in validated_stix_bundles.items()}
        return filtered_stix_bundles, message
    else:
        return validated_stix_bundles, message

def extract_ids_to_be_replaced(stix_bundle:dict) -> dict:
    """Creates a dictionary where keys are all the ids identified in a stix_bundle
    and values are the upadated ids according to the rule:
    File ids -> type--hashes
    SDO ids -> type--name
    SCO ids -> type--value
    SRO ids -> type--source_ref--relationship_type--new_id_target_ref
    """
    ids_mapping = {}
    sro_objects = []

    # SDO and SCO ids should be extracted as they are also used in SROs
    for stix_object in stix_bundle["objects"]:
        filterd_stix_object = smap(stix_object)
        old_id = filterd_stix_object.id
        if isinstance(filterd_stix_object, File):
            new_id = filterd_stix_object.type + "--" + filterd_stix_object.hashes["SHA-256"]
            ids_mapping[old_id] = new_id
        elif isinstance(filterd_stix_object, SDO):
            new_id = filterd_stix_object.type + "--" + filterd_stix_object.name
            ids_mapping[old_id] = new_id
        elif isinstance(filterd_stix_object, SCO):
            new_id = filterd_stix_object.type + "--" + filterd_stix_object.value
            ids_mapping[old_id] = new_id
        else:
            sro_objects.append(filterd_stix_object)

    # SRO ids extraction
    for sro in sro_objects:
        old_id = sro.id
        new_id_source_ref = ids_mapping[sro.source_ref]
        new_id_target_ref = ids_mapping[sro.target_ref]
        new_id = sro.type + "--" + new_id_source_ref + "--" + sro.relationship_type + "--" + new_id_target_ref
        ids_mapping[old_id] = new_id

    return ids_mapping

def create_new_ids(stix_bundle:dict) -> dict:
    """Creates a STIX bundle with new ids"""
    new_stix_bundle_id = ""
    new_stix_bundle_type = stix_bundle["type"]

    # Create an id mapping
    ids_mapping = extract_ids_to_be_replaced(stix_bundle)

    # Create objects with new ids
    new_stix_bundle_objects = []
    for obj in stix_bundle["objects"]:
        new_object = copy.deepcopy(obj)
        new_object["id"] = ids_mapping[obj["id"]]
        if "source_ref" in new_object.keys():
            new_object["source_ref"] = ids_mapping[obj["source_ref"]]
        if "target_ref" in new_object.keys():
            new_object["target_ref"] = ids_mapping[obj["target_ref"]]
        if "object_refs" in new_object.keys():
            new_object["object_refs"] = list(ids_mapping.values())
        new_stix_bundle_objects.append(new_object)

    # Create a new bundle
    new_stix_bundle = {
        "id":new_stix_bundle_id,
        "type":new_stix_bundle_type,
        "objects":new_stix_bundle_objects
    }

    return new_stix_bundle

def create_bundles_with_new_ids(stix_bundles:dict) -> dict:
    """Creates a dictionary os STIX bundles were all ids are replaced
    using the function create_new_ids(). Keys are the names of the bundles
    and values are the data in both input and output."""
    return {k:create_new_ids(v) for k, v in stix_bundles.items()}

def keep_only_object_type(objects_in_example: list, type: str) -> list:
    """Removes all objects of different type than the one specified.
    The input is a list of objects"""
    objects_to_return = []
    for obj in objects_in_example:
        if "type" in obj.keys():
            if obj["type"]==type:
                objects_to_return.append(obj)
            else:
                continue
        elif "relationship_type" in obj.keys():
            if type=="relationship":
                objects_to_return.append(obj)
            else:
                continue
        else:
            raise ValueError(f"Cannot identify Object type of: {obj}")
    return objects_to_return

def save_stix_bundles(stix_bundles:dict, config) -> None:
    """Save STIX bundles given in a dict format where keys are the
    names of the bundle and values are the data."""

    save_path = config["processed_stix_bundles_path"]
    split_in_sdo_types = config["split_stix_types_in_saving"]

    # Save the complete bundles
    if not os.path.exists(os.path.join(save_path, "complete_bundles")):
        os.mkdir(os.path.join(save_path, "complete_bundles"))

    for k, v in stix_bundles.items():
        save_bundle(os.path.join(save_path, "complete_bundles"), k, v)

    # Save by splitting in types
    if split_in_sdo_types:
        for t in split_in_sdo_types:
            if not os.path.exists(os.path.join(save_path, t)):
                os.mkdir(os.path.join(save_path, t))
            for k, v in stix_bundles.items():
                data = {"objects":keep_only_object_type(v["objects"], t)}
                save_bundle(os.path.join(save_path, t), k, data)