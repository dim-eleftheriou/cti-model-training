import os
import json
import _utils

mitre_attack_path = "C:/Users/eleftheriou/Desktop/data/mitre_attack_knowledge_base"
for sector in os.listdir(mitre_attack_path):
    pattern_path = os.path.join(mitre_attack_path, sector)
    for pattern in os.listdir(pattern_path):
        object_folder_path = os.path.join(pattern_path, pattern)
        for obj in os.listdir(object_folder_path):
            with open(os.path.join(object_folder_path, obj, obj + ".json"), mode="r", encoding="utf-8") as f:
                bundle = json.load(f)

            filtered_bundle = {
                "type":bundle["type"],
                "id":bundle["id"],
                "objects":_utils.filter_lists_of_bundle_fields(bundle["objects"])
            }

            with open(os.path.join(pattern_path, obj + ".json"), mode="w", encoding="utf-8") as f:
                json.dump(filtered_bundle, f)