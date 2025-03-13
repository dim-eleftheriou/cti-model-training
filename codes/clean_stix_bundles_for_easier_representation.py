import os
import json

task_folder = "C:/Users/eleftheriou/Desktop/train_data/llm_batched_data/lower_level_tasks/"
tasks = ["attack-pattern", "malware"]

keep_keys = ["id",
             "spec_version",
             "name",
             "external_references",
             "type",
             "object_marking_refs",
             "relationship_type",
             "source_ref",
             "target_ref",
             "description",
             "identity_class"]

for t in tasks:
    for bundle in os.listdir(os.path.join(task_folder, t)):
        file_path = os.path.join(task_folder, t, bundle)
        with open(file_path, mode="r", encoding="utf-8") as file:
            data = json.load(file)
        for i, output in enumerate(data["output"]):
            drop_keys = set(list(output.keys())).difference(set(keep_keys))
            for key in drop_keys:
                del data["output"][i][key]
        with open(file_path, mode="w", encoding="utf-8") as file:
            json.dump(data, file)