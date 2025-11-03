import os
import time
import logging
from .trials import extract_top_trials
from src.utils.xml_parsing import xml_processing
from src.utils.json import load_json, save_json
from src.utils.model_api import prompt_model
from src.utils.config import MODEL_PROVIDER, MODEL_NAME, OPENAI_API_KEY

# Configure logging for detailed output.
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def generate_coarse_labelling(prompt_base, inclusion, exclusion, topic_description, model, provider=None, api_key=None):
    prompt = f"{prompt_base}\n{inclusion}\n{exclusion}\n(Patient profile):\n{topic_description}"
    if provider is None:
        provider = MODEL_PROVIDER
    if api_key is None:
        api_key = OPENAI_API_KEY
    return prompt_model(prompt, model, provider=provider, api_key=api_key)

def coarse_labelling(topic_dir, xml_trials_dir, results_dir, prompt_dir, qrel_results_dir, model, top_n, provider=None, api_key=None):
    qrel_results_path = os.path.join(qrel_results_dir, "qrel.txt")
    topic_trials, _ = extract_top_trials(qrel_results_path, top_n)
    output_path = os.path.join(results_dir, "coarse_labelling.json")
    topic_description_dict = load_json(topic_dir)
    prompt_path = os.path.join(prompt_dir, "coarse_labelling_prompt.txt")

    with open(prompt_path, 'r') as f:
        prompt_base = f.read()

    if os.path.exists(output_path):
        coarse_labels = load_json(output_path)
    else:
        coarse_labels = {topic_id: {} for topic_id in topic_trials.keys()}

    # Calculate total number of trials to process for progress logging.
    total_trials = sum(len(trials) for trials in topic_trials.values())
    logging.info(f"Processing {total_trials} trials for coarse labelling")
    overall_counter = 0
    overall_start_time = time.time()

    for topic_id, trials in topic_trials.items():
        topic_description = topic_description_dict.get(topic_id, "No topic description found")
        for trial_id in trials:

            if trial_id in coarse_labels[topic_id]:
                overall_counter += 1
                continue

            trial_start_time = time.time()
            trial_file_path = os.path.join(xml_trials_dir, trial_id + ".xml")
            if not os.path.exists(trial_file_path):
                logging.warning(f"Trial {trial_id} does not exist in the trials directory")
                continue

            try:
                inclusion, exclusion, _ = xml_processing(trial_file_path)
            except Exception as e:
                logging.error(f"Error processing XML for trial {trial_id}: {e}")
                continue

            label = generate_coarse_labelling(prompt_base, inclusion, exclusion, topic_description, model, provider, api_key)
            if topic_id not in coarse_labels:
                coarse_labels[topic_id] = {}
            coarse_labels[topic_id][trial_id] = label

            overall_counter += 1
            processing_time = time.time() - trial_start_time
            overall_progress = (overall_counter / total_trials) * 100
            logging.info(f"Trial {trial_id} processed in {processing_time:.2f} seconds - {overall_progress:.2f}% complete")
            save_json(coarse_labels, output_path)

    total_elapsed = time.time() - overall_start_time
    logging.info(f"All trials processed in {total_elapsed:.2f} seconds")






