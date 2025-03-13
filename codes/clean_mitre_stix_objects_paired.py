import os
import utils

mitre_stix_data_path = "C:/Users/eleftheriou/Desktop/data/scraped_mitre_w_stix_pairs/without_filtering_applied_to_stix"
processed_mitre_stix_data_path = "C:/Users/eleftheriou/Desktop/data/scraped_mitre_w_stix_pairs/with_filtering_applied_to_stix"

if not os.path.exists(processed_mitre_stix_data_path):
    os.mkdir(processed_mitre_stix_data_path)

stix_bundles = utils.read_bundles_in_path(mitre_stix_data_path)
filtered_bundles = {k:{"type":v["output"]["type"],
                       "id":v["output"]["id"],
                       "objects":utils.filter_lists_of_bundle_fields(v["output"]["objects"])} for k, v in stix_bundles.items()}

for k in filtered_bundles.keys():
    inputs = stix_bundles[k]["input"]
    outputs = filtered_bundles[k]
    data = {"input":inputs,
            "output":outputs}
    utils.save_bundle(processed_mitre_stix_data_path, k, data)