from utils import create_final_dataset
import pandas as pd
import shutil
import os

# Pipeline for creating the dataset
initial_data_path = "C:/Users/AIAS/Documents/cti-model-training/data/reports"
formatted_data_path = "C:/Users/AIAS/Documents/cti-model-training/data/reports_formatted/raw/english"
alienvault_data_path = "C:/Users/AIAS/Documents/cti-model-training/data/reports_formatted/alienvault"
failure_message = "REPORT IS NOT EXTRACTED! Reason caused the failure:"

# Read references for finding all data
report_names = pd.read_csv("C:/Users/AIAS/Documents/cti-model-training/data/opencti_reports_external_references.csv")["ID"].tolist()

# Create the final directory to store data
final_data_path = "C:/Users/AIAS/Documents/cti-model-training/data/final_reports"
if os.path.exists(final_data_path):
    shutil.rmtree(final_data_path)
os.makedirs(final_data_path)

create_final_dataset(report_names,
                     initial_data_path,
                     formatted_data_path,
                     alienvault_data_path,
                     final_data_path)