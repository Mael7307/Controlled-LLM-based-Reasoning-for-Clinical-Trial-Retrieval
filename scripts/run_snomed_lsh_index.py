import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.build_SNOMED import build_lsh_index
from src.utils.config import SNOMED_PATH, SNOMED_INDEX_PATH

def main():
    build_lsh_index.build_index(
        snomed_path= SNOMED_PATH,
        output_dir= SNOMED_INDEX_PATH
    )


if __name__ == "__main__":
    main()

