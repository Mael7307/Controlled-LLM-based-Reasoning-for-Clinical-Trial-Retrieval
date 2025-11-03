import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.utils.evaluation import evaluate_qrel
from src.utils.config import TREC_QRELS_PATH


def main():
    qrel_results_path = input("Enter the path to the QREL results file: ").strip()
    if qrel_results_path.startswith('"') and qrel_results_path.endswith('"'):
        qrel_results_path = qrel_results_path[1:-1]
    qrel_results_path = os.path.normpath(qrel_results_path)
    evaluate_qrel(
        qrel_results_path = qrel_results_path,
        qrel_file = TREC_QRELS_PATH
    )

if __name__ == "__main__":
    main()
