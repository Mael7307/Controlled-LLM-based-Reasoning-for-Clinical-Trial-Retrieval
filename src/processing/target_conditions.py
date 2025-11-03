import os
from src.utils.xml_parsing import *
import glob
from src.utils.json import save_json

def build_target_conditions(xml_files_dir, output_dir):

    # Use glob to retrieve all XML file paths
    xml_file_paths = glob.glob(os.path.join(xml_files_dir, '*.xml'))
    total_files = len(xml_file_paths)

    # Dictionary to store conditions and corresponding file names
    conditions = {}

    for idx, xml_file in enumerate(xml_file_paths, start=1):
        inclusion, exclusion, extracted_elements = xml_processing(xml_file)

        # Retrieve lists or default to empty lists if None
        condition_list = extracted_elements.get('condition') or []
        conditions_browse_list = extracted_elements.get('condition_browse') or []
        keywords_list = extracted_elements.get('keyword') or []

        # Combine all condition-related lists
        aggregate_list = condition_list + conditions_browse_list + keywords_list

        # Add the file (using basename) to each condition found in the aggregate list
        for condition in aggregate_list:
            conditions.setdefault(condition, []).append(os.path.basename(xml_file))

        # Print progress percentage
        progress = (idx / total_files) * 100
        print(f"Progress: {progress:.2f}% ({idx}/{total_files} files processed)", end="\r")


    # Write the conditions dictionary to a JSON file
    save_json(conditions, output_dir)

