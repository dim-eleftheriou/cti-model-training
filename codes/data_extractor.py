import shutil
import json
import os

data_path = "C:/Users/deleftheriou/Documents/Development/cti"
# Find the directories of stix bundles
stix_dirs = [f for f in os.listdir(data_path) if "." not in f and f!="venv"]

# Create a new directory for saving the data for training
save_path = os.path.join(data_path, "mitre_attack_knowledge_base")
if save_path not in os.listdir(data_path):
    os.mkdir(save_path)

# Copy the stix directories in the mitre_attack_knowledge_base
for d in stix_dirs:
    shutil.copytree(os.path.join(data_path, d), os.path.join(save_path, d))

def format_data(dir):
    # Create a folder for each category and bundle
    for bundle in os.listdir(dir):
        bundle_name = bundle.split(".json")[0]
        os.mkdir(os.path.join(dir, bundle_name))

        # Read the stix bundle
        with open(os.path.join(dir, bundle), encoding="utf8") as f:
            bundle_data = json.load(f)

        # Save the description in a txt
        with open(os.path.join(dir, bundle_name, "description.txt"), "w", encoding="utf8") as f:
            if "description" in bundle_data["objects"][0].keys():
                f.write(bundle_data["objects"][0]["description"])

        # Save the name in a txt
        with open(os.path.join(dir, bundle_name, "name.txt"), "w", encoding="utf8") as f:
            if "name" in bundle_data["objects"][0].keys():
                f.write(bundle_data["objects"][0]["name"])

        # Save the references in a json
        with open(os.path.join(dir, bundle_name, "references.json"), "w", encoding="utf8") as f:
            if "external_references" in bundle_data["objects"][0].keys():
                json.dump({"external_references":bundle_data["objects"][0]["external_references"]}, f)

        # Copy the stix bundle
        shutil.move(os.path.join(dir, bundle),
                        os.path.join(dir, bundle_name, bundle))
        
def dir_format_data(dir):
    print(f"Formating directory: {dir}")
    for d in os.listdir(dir):
        workdir = os.path.join(dir, d)
        if os.path.isfile(workdir):
            continue
        format_data(workdir)

for fdir in os.listdir(save_path):
    if fdir=="capec":
        for subdir in os.listdir(os.path.join(save_path, fdir)):
            workdir = os.path.join(save_path, fdir, subdir)
            dir_format_data(workdir)
    else:
        workdir = os.path.join(save_path, fdir)
        dir_format_data(workdir)