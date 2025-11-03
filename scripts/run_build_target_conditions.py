import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.processing import target_conditions
from src.utils.config import TRIALS_XML_DIR, CONDITIONS_JSON_PATH


def main():
    target_conditions.build_target_conditions(
        xml_files_dir=TRIALS_XML_DIR,
        output_dir=CONDITIONS_JSON_PATH
    )

if __name__ == "__main__":
    main()
