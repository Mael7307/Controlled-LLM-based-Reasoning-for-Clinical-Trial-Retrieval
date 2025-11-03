import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.utils.initial_retrieval import run_initial_retrieval
from src.utils.SNOMED_retrieval import load_ontology
from src.utils.config import (TREC_QRELS_PATH, TOPIC_DIR, RESULTS_DIR, DEPTH, TRIALS_XML_DIR,
                              MAPPED_DIAGNOSES_PATH, MAPPED_CONDITIONS_PATH, STRUCTURED_TOPIC_DIR)


def main():
    SNOMEDCT_US = load_ontology()
    run_initial_retrieval(
        diagnoses_mapping_path=MAPPED_DIAGNOSES_PATH,
        conditions_mapping_path=MAPPED_CONDITIONS_PATH,
        retrieval_depth=DEPTH,
        qrels_path=TREC_QRELS_PATH,
        trials_xml_directory=TRIALS_XML_DIR,
        topic_directory=TOPIC_DIR,
        SNOMEDCT_US=SNOMEDCT_US,
        results_directory=RESULTS_DIR,
        structured_topics_dir = STRUCTURED_TOPIC_DIR
    )

if __name__ == "__main__":
    main()
