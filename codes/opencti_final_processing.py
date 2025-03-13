import re
import os
import json

reports_path = "C:/Users/eleftheriou/Desktop/data/opencti/reports/with_image_descriptions"
stix_bundles_path = "C:/Users/eleftheriou/Desktop/data/opencti/bundles/filtered"
filtered_dirs = os.listdir("C:/Users/eleftheriou/Desktop/data/opencti/bundles/filtered")
save_path = "C:/Users/eleftheriou/Desktop/data/opencti/input_output_pairs/filtered_stix_bundles"

if not os.path.exists(save_path):
    os.mkdir(save_path)

for dir in filtered_dirs:
    if os.path.exists(os.path.join(save_path, dir)):
        continue
    else:
        os.mkdir(os.path.join(save_path, dir))

for report in os.listdir(reports_path):

    try:
        with open(os.path.join(reports_path, report), mode="r", encoding="utf-8") as file:
            data = file.read()

        data = re.sub(r'external_reference_url_\d+', '', data)
        data = data.strip()

        bundle_name = report.split(".txt")[0]

        for dir in filtered_dirs:
            with open(os.path.join(stix_bundles_path, dir, bundle_name + ".json"), mode="r", encoding="utf-8") as file:
                stix_data = json.load(file)

            save_dict = {"input":data,
                        "output":stix_data}
    
            with open(os.path.join(save_path, dir, bundle_name + ".json"), mode="w", encoding="utf-8") as file:
                json.dump(save_dict, file)
    except:
        print(report)
    
