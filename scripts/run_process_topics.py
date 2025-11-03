import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.processing import topics
from src.utils.config import TOPIC_PROMPT_PATH, TOPICS_XML_PATH, RESULTS_DIR, MODEL_NAME, MODEL_PROVIDER, OPENAI_API_KEY


def main():
    topics.process_topics(
        topic_prompt_path=TOPIC_PROMPT_PATH,
        topics_xml_path=TOPICS_XML_PATH,
        results_dir=RESULTS_DIR,
        model_name=MODEL_NAME,
        provider=MODEL_PROVIDER,
        api_key=OPENAI_API_KEY
    )

if __name__ == "__main__":
    main()


