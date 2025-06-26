import os
import yaml
import logging
from utils import (read_bundles_in_path, 
                   filter_bundles, 
                   create_bundles_with_new_ids, 
                   save_stix_bundles)

logging_filename = "stix_processing.log"
if os.path.exists(logging_filename):
    os.remove(logging_filename)

# Set up logging
logging.basicConfig(
    filename=logging_filename,
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def set_configuration():
    logger.info("Reading configuration...")

    with open("config.yaml", "r") as file:
        config = yaml.safe_load(file)

    if not os.path.exists(config["processed_stix_bundles_path"]):
        os.mkdir(config["processed_stix_bundles_path"])
        logger.info(f'Created directory: {config["processed_stix_bundles_path"]}')

    return config

def main():
    logger.info("Starting STIX bundle processing.")
    # Read configuration parameters
    config = set_configuration()
    # Read data
    logger.info("Reading STIX bundles...")
    stix_bundles = read_bundles_in_path(config["raw_stix_bundles_path"])
    # Remove useless fields from STIX objects as well as unnecessary objects
    logger.info("Filtering STIX bundles...")
    filtered_bundles, validation_message = filter_bundles(stix_bundles, config)
    if validation_message:
        logger.info(validation_message)
    # Set new ids
    logger.info("Assigning new IDs...")
    filtered_bundles_w_new_ids = create_bundles_with_new_ids(filtered_bundles)
    # Save in complete and splitted forms
    logger.info("Saving processed STIX bundles...")
    save_stix_bundles(filtered_bundles_w_new_ids, config)
    logger.info("Processing complete.")


if __name__ == "__main__":
    main()