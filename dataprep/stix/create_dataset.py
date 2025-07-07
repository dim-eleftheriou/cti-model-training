import os
import yaml
import random
from utils import read_bundles_in_path, save_bundle

def read_report(filepath:str, filename:str):
    with open(os.path.join(filepath, filename), mode="r", encoding="utf-8") as f:
        report = f.read()
    return report

def read_training_examples(file_abs_path:str):
    with open(file_abs_path, "r") as f:
        training_examples = f.read()
    return training_examples.split("\n")
    
    
if __name__=="__main__":
    with open("config.yaml", "r") as file:
        config = yaml.safe_load(file)

    if not os.path.exists(config["io_save_path"]):
        os.mkdir(config["io_save_path"])
        os.mkdir(os.path.join(config["io_save_path"], "train"))
        os.mkdir(os.path.join(config["io_save_path"], "validation"))
        os.mkdir(os.path.join(config["io_save_path"], "test"))


    training_examples = read_training_examples(config["training_examples_file"])

    bundles = read_bundles_in_path(config["input_path"])
    available_reports = os.listdir(config["output_path"])
    
    for bundle_name, output in bundles.items():

        if bundle_name.split(".json")[0] not in training_examples:
            continue

        # Create the name of the report. Same but with suffix .txt
        report_name = bundle_name.split(".json")[0] + ".txt"

        # Read report
        if report_name in available_reports:

            report = read_report(config["output_path"], report_name)

            # Create data point
            example = {
                    "input":report,
                    "output":output
            }

            rn = random.random()
            # Randomly select destination
            if rn<=0.8:
                used_for = "train"
            elif rn<=0.9:
                used_for = "validation"
            else:
                used_for = "test"

            save_path = os.path.join(config["io_save_path"], used_for)

            # Save in .json format
            save_bundle(save_path, bundle_name, example)

    