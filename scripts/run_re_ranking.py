import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.processing import re_ranking
from src.utils.config import RESULTS_DIR, TREC_QRELS_PATH


def main():
    re_ranking.re_ranking_and_evaluation(
        results_path=RESULTS_DIR,
        qrel_file=TREC_QRELS_PATH
    )

if __name__ == "__main__":
    main()