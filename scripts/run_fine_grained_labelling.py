import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.processing import fine_grained_labelling
from src.utils.config import TOP_N, RESULTS_DIR, MODEL_NAME, MODEL_PROVIDER, OPENAI_API_KEY, INITIAL_RETRIEVAL_DIR, PROMPT_DIR


def main():
    print("Running fine-grained labelling")
    fine_grained_labelling.fine_grained_labelling(
        qrel_results_dir=INITIAL_RETRIEVAL_DIR,
        results_dir=RESULTS_DIR,
        prompt_dir=PROMPT_DIR,
        model=MODEL_NAME,
        top_n=TOP_N,
        provider=MODEL_PROVIDER,
        api_key=OPENAI_API_KEY
    )

if __name__ == "__main__":
    main()
