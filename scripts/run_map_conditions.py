import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.build_SNOMED import map
from src.utils.config import SNOMED_INDEX_PATH, CONDITIONS_JSON_PATH, SNOMED_PATH, MAPPED_CONDITIONS_PATH


def main():
    map.build_map(
        index_dir=SNOMED_INDEX_PATH,
        conditions_dir=CONDITIONS_JSON_PATH,
        snomed_dict_dir=SNOMED_PATH,
        output_dir=MAPPED_CONDITIONS_PATH)

if __name__ == "__main__":
    main()
