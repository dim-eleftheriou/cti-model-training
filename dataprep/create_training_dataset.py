from utils import replace_pictures, augment_unscraped_refs
import pandas as pd
import shutil
import os

# Pipeline for creating the dataset
initial_data_path = "C:/Users/AIAS/Documents/cti-model-training/data/reports"
formatted_data_path = "C:/Users/AIAS/Documents/cti-model-training/data/reports_formatted/raw"
alienvault_data_path = "C:/Users/AIAS/Documents/cti-model-training/data/reports_formatted/alienvault"
failure_message = "REPORT IS NOT EXTRACTED! Reason caused the failure:"

# Read references for finding all data
report_names = pd.read_csv("data/opencti_reports_external_references.csv")["ID"].tolist()

# Create the final directory to store data
final_data_path = "C:/Users/AIAS/Documents/cti-model-training/data/final_reports"
if os.path.exists(final_data_path):
    shutil.rmtree(final_data_path)
os.makedir(final_data_path)

# For reports that are not scraped check if initial data exist
augment_unscraped_refs(report_names, initial_data_path, formatted_data_path, failure_message)

# For every report we should replace the pictures <!-- image -->
replace_pictures(initial_data_path, formatted_data_path) # Some reports contain more references

# 
