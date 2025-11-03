import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.processing import map_diagnoses
from src.utils.SNOMED_retrieval import load_ontology
from src.utils.config import LSH_INDEX_PATH, SNOMED_PATH, PROCESSED_TOPICS_PATH, MAPPED_DIAGNOSES_PATH


def main():
    SNOMEDCT_US = load_ontology()
    map_diagnoses.diagnoses_map(
        index_dir=LSH_INDEX_PATH,
        snomed_dict_dir=SNOMED_PATH,
        processed_topic_dir=PROCESSED_TOPICS_PATH,
        output_dir=MAPPED_DIAGNOSES_PATH,
        SNOMEDCT_US=SNOMEDCT_US
    )

if __name__ == "__main__":
    main()