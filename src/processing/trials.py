import os
import time
import logging
from src.utils.xml_parsing import xml_processing
from src.utils.model_api import prompt_model
from src.utils.config import MODEL_PROVIDER, OPENAI_API_KEY
from src.utils.json import load_json, save_json

# Configure logging for detailed output.
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def extract_top_trials(file_path, n):
    """
    Extracts the top N trials per topic from the given qrel file.

    Parameters:
        file_path (str): Path to the qrel file.
        n (int): Maximum rank to include.

    Returns:
        tuple: A dictionary mapping topic_id to list of trial_ids, and a set of unique trial_ids.
    """
    topic_trials = {}
    trials_to_process = set()
    with open(file_path, 'r') as f:
        for line in f:
            parts = line.strip().split()
            if not parts or len(parts) < 4:
                continue
            topic_id, _, trial_id, rank_str = parts[0], parts[1], parts[2], parts[3]
            try:
                rank = int(rank_str)
            except ValueError:
                logging.warning(f"Invalid rank '{rank_str}' in line: {line.strip()}")
                continue
            if rank <= n:
                topic_trials.setdefault(topic_id, []).append(trial_id)
                trials_to_process.add(trial_id)
    return topic_trials, trials_to_process


def generate_structure(criteria, model, prompt_base, provider=None, api_key=None):
    """
    Generates structured text from criteria using the specified model.

    Parameters:
        criteria (str): The criteria text.
        model (str): The model to use.
        prompt_base (str): The base prompt text.
        provider (str): The provider to use ("ollama" or "openai").
        api_key (str): Optional API key for OpenAI.

    Returns:
        str: The structured text output.
    """
    if not criteria:
        return ""
    prompt = f"{prompt_base}\nInput: {criteria}"
    if provider is None:
        provider = MODEL_PROVIDER
    if api_key is None:
        api_key = OPENAI_API_KEY
    return prompt_model(prompt, model, provider=provider, api_key=api_key)


def process_trials(qrel_results_dir, xml_trials_dir, results_dir, prompt_dir, model, top_n, provider=None, api_key=None):
    """
    Processes the trials by extracting information from XML files and generating structured
    text using an external model.

    Parameters:
        qrel_results_dir (str): Directory containing the qrel results file.
        xml_trials_dir (str): Directory containing XML trial files.
        results_dir (str): Directory where results are saved.
        prompt_dir (str): Directory containing the prompt file.
        model (str): The model to use for structuring the trials.
        top_n (int): The maximum trial rank to process.
    """
    output_path = os.path.join(results_dir, "structured_trials.json")
    prompt_path = os.path.join(prompt_dir, "trial_structure_prompt.txt")
    qrel_results_path = os.path.join(qrel_results_dir, "qrel.txt")

    _, trials_to_process = extract_top_trials(qrel_results_path, top_n)
    total_trials = len(trials_to_process)
    logging.info(f"Processing {total_trials} trials")

    with open(prompt_path, 'r') as f:
        prompt_base = f.read()

    if os.path.exists(output_path):
        structured_trials = load_json(output_path)
    else:
        structured_trials = {}

    overall_start_time = time.time()

    # Process trials in a sorted order for consistency.
    for idx, trial in enumerate(sorted(trials_to_process), start=1):
        trial_start_time = time.time()
        trial_path = os.path.join(xml_trials_dir, trial + ".xml")
        if not os.path.exists(trial_path):
            logging.warning(f"Trial {trial} does not exist in the trials directory")
            continue

        try:
            inclusion, exclusion, _ = xml_processing(trial_path)
        except Exception as e:
            logging.error(f"Error processing XML for trial {trial}: {e}")
            continue

        structured_inclusion = generate_structure(inclusion, model, prompt_base, provider, api_key)
        structured_exclusion = generate_structure(exclusion, model, prompt_base, provider, api_key)
        processing_time = time.time() - trial_start_time

        structured_trials[trial] = {
            "inclusion": structured_inclusion,
            "exclusion": structured_exclusion
        }
        save_json(structured_trials, output_path)

        overall_progress = (idx / total_trials) * 100
        logging.info(f"Trial {trial} processed in {processing_time:.2f} seconds - {overall_progress:.2f}% complete")

    total_elapsed = time.time() - overall_start_time
    logging.info(f"All trials processed in {total_elapsed:.2f} seconds")












