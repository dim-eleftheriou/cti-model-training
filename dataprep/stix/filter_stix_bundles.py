import os
import _utils

mitre_stix_data_path = "C:/Users/AIAS/Desktop/backup/data/opencti/bundles/raw"
filtered_mitre_stix_data_path = "C:/Users/AIAS/Desktop/backup/data/opencti/bundles/filtered_correct"

if not os.path.exists(filtered_mitre_stix_data_path):
    os.mkdir(filtered_mitre_stix_data_path)

stix_bundles = _utils.read_bundles_in_path(mitre_stix_data_path)
filtered_bundles = {k:{"type":v["type"],
                       "id":v["id"],
                       "objects":_utils.filter_lists_of_bundle_fields(v["objects"])} for k, v in stix_bundles.items()}

filtered_bundles = {k:_utils.replace_ids_in_bundle(v) for k, v in filtered_bundles.items()}

os.mkdir(os.path.join(filtered_mitre_stix_data_path, "complete_bundles"))
for k, v in filtered_bundles.items():
    _utils.save_bundle(os.path.join(filtered_mitre_stix_data_path, "complete_bundles"), k, v)

# Types of bundles
types = [
    'identity', 'report', 'relationship',
    'indicator', 'file', 'malware', 'attack-pattern', 'domain-name',
    'intrusion-set', 'url', 'vulnerability', 'location', 'hostname',
    'cryptocurrency-wallet', 'email-addr', 'ipv4-addr'
    ]

for t in types:
    os.mkdir(os.path.join(filtered_mitre_stix_data_path, t))
    for k, v in filtered_bundles.items():
        data = {"objects":_utils.filter_object_type(v["objects"], t)}
        _utils.save_bundle(os.path.join(filtered_mitre_stix_data_path, t), k, data)

