import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.processing import coarse_labelling
from src.utils.config import TOPIC_DIR, TRIALS_XML_DIR, RESULTS_DIR, PROMPT_DIR, INITIAL_RETRIEVAL_DIR, MODEL_NAME, MODEL_PROVIDER, OPENAI_API_KEY, TOP_N


def main():
    coarse_labelling.coarse_labelling(
        topic_dir=TOPIC_DIR,
        xml_trials_dir=TRIALS_XML_DIR,
        results_dir=RESULTS_DIR,
        prompt_dir=PROMPT_DIR,
        qrel_results_dir=INITIAL_RETRIEVAL_DIR,
        model=MODEL_NAME,
        top_n=TOP_N,
        provider=MODEL_PROVIDER,
        api_key=OPENAI_API_KEY
    )

if __name__ == "__main__":
    main()


