import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.processing import trials
from src.utils.config import INITIAL_RETRIEVAL_DIR, TRIALS_XML_DIR, RESULTS_DIR, PROMPT_DIR, MODEL_NAME, MODEL_PROVIDER, OPENAI_API_KEY, TOP_N


def main():
    trials.process_trials(
        qrel_results_dir=INITIAL_RETRIEVAL_DIR,
        xml_trials_dir=TRIALS_XML_DIR,
        results_dir=RESULTS_DIR,
        prompt_dir=PROMPT_DIR,
        model=MODEL_NAME,
        top_n=TOP_N,
        provider=MODEL_PROVIDER,
        api_key=OPENAI_API_KEY
    )

if __name__ == "__main__":
    main()
