import os
import xml.etree.ElementTree as ET
import time
from src.utils.model_api import prompt_model
from src.utils.config import MODEL_PROVIDER, OPENAI_API_KEY
from src.utils.json import *


def process_topics(topic_prompt_path, topics_xml_path, results_dir, model_name, max_retries=10000, delay_seconds=60, provider=None, api_key=None):
    """
    Processes topics using a system prompt and writes each output to a file,
    calling a model specified by model_name and provider.

    Args:
        topic_prompt_path (str): Path to the file containing the system prompt.
        topics_xml_path (str): Path to the XML file with topics.
        results_dir (str): Directory where processed topic files will be saved.
        model_name (str): The model name to use.
        max_retries (int): Maximum number of retry attempts on failure.
        delay_seconds (int): Delay (in seconds) between retry attempts.
        provider (str): The provider to use ("ollama" or "openai").
        api_key (str): Optional API key for OpenAI.
    """
    # Ensure output directory exists
    os.makedirs(results_dir, exist_ok=True)

    # Load system prompt
    with open(topic_prompt_path, 'r', encoding='utf-8') as f:
        system_prompt = f.read()

    # Parse the topics XML file
    tree = ET.parse(topics_xml_path)
    root = tree.getroot()

    topics = []
    for topic_element in root.findall('topic'):
        number = int(topic_element.get('number'))
        description = topic_element.text.strip()
        topics.append((number, description))

    retry = 0
    processsed_topics = {}
    for idx, (number, topic) in enumerate(topics):
        print(f"Processing Topic number: {number}. Remaining topics: {len(topics) - idx - 1}")
        user_prompt = f"Input: {topic}"
        full_prompt = system_prompt + user_prompt

        try:
            # Call the model using the specified provider
            if provider is None:
                current_provider = MODEL_PROVIDER
            else:
                current_provider = provider
            if api_key is None:
                current_api_key = OPENAI_API_KEY
            else:
                current_api_key = api_key
            output = prompt_model(full_prompt, model=model_name, provider=current_provider, api_key=current_api_key)
            processsed_topics[number] = output
            save_json(processsed_topics, f"{results_dir}/processed_topics.json")


        except Exception as e:
            print(f"Error processing topic {number}: {e}")
            if retry < max_retries:
                print(f"Retrying in {delay_seconds} seconds...")
                time.sleep(delay_seconds)
                retry += 1
            else:
                print("Max retries reached. Skipping topic.")