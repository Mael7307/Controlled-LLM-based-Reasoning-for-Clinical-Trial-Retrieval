from src.utils.json import *
import os
import re
import time
import logging
import json
from .trials import extract_top_trials
from src.utils.model_api import prompt_model
from src.utils.config import MODEL_PROVIDER, OPENAI_API_KEY


def fine_grained_labelling(qrel_results_dir, results_dir, prompt_dir, model, top_n, provider=None, api_key=None):
    """
    Processes trial data to generate fine-grained labels for each trial based on inclusion and exclusion criteria.
    """
    qrel_results_path = os.path.join(qrel_results_dir, "qrel.txt")
    trials_by_topic, _ = extract_top_trials(qrel_results_path, top_n)
    output_path = os.path.join(results_dir, "fine_labelling.json")
    structured_trials_path = os.path.join(results_dir, "structured_trials.json")
    structured_trials = load_json(structured_trials_path)
    processed_topics_path = os.path.join(results_dir, "processed_topics.json")
    processed_topics = load_json(processed_topics_path)
    topics = extract_categorised_topics(processed_topics)

    fine_labels = load_json(output_path) if os.path.exists(output_path) else {topic_id: {} for topic_id in trials_by_topic.keys()}

    total_trials = sum(len(trial_ids) for trial_ids in trials_by_topic.values())
    logging.info(f"Processing {total_trials} trials for fine labelling")
    overall_counter = 0
    overall_start_time = time.time()

    for topic_id, trial_ids in trials_by_topic.items():
        topic = topics.get(topic_id)
        fine_labels.setdefault(topic_id, {})
        for trial_id in trial_ids:
            if trial_id in fine_labels[topic_id]:
                overall_counter += 1
                continue

            trial_start_time = time.time()
            raw_trial = structured_trials.get(trial_id)
            if raw_trial is None:
                logging.warning(f"Trial {trial_id} does not exist in the structured trials file")
                continue

            trial = extract_categorised_criteria(raw_trial)
            fine_labels[topic_id][trial_id] = generate_fine_labelling(topic, trial, prompt_dir, model, provider, api_key)
            overall_counter += 1

            processing_time = time.time() - trial_start_time
            overall_progress = (overall_counter / total_trials) * 100
            logging.info(f"Trial {trial_id} processed in {processing_time:.2f} seconds - {overall_progress:.2f}% complete")
            save_json(fine_labels, output_path)

    total_elapsed = time.time() - overall_start_time
    logging.info(f"All trials processed in {total_elapsed:.2f} seconds")


def generate_fine_labelling(topic, trial, prompt_dir, model, provider=None, api_key=None):
    """
    Generates fine-grained labels for a trial using inclusion and exclusion criteria along with topic context.
    """
    # Mapping from trial criteria keys to corresponding topic keys.
    trial_to_topic_map = {
        "demographic criteria": "demographic characteristics",
        "disease criteria": "disease characteristics",
        "prior treatment criteria": "prior treatment"
    }

    def get_topic_key(trial_key):
        return trial_to_topic_map.get(trial_key)

    inclusion_prompt_path = os.path.join(prompt_dir, "inclusion_fine_labelling_prompt.txt")
    exclusion_prompt_path = os.path.join(prompt_dir, "exclusion_fine_labelling_prompt.txt")
    inclusion_dict = trial.get("inclusion", {})
    exclusion_dict = trial.get("exclusion", {})

    # Load prompt templates.
    with open(inclusion_prompt_path, 'r') as f:
        inclusion_prompt_base = f.read()
    with open(exclusion_prompt_path, 'r') as f:
        exclusion_prompt_base = f.read()

    def process_criteria(criteria_dict, prompt_base):
        labels = {}
        if provider is None:
            current_provider = MODEL_PROVIDER
        else:
            current_provider = provider
        if api_key is None:
            current_api_key = OPENAI_API_KEY
        else:
            current_api_key = api_key
        for criteria_type, criteria_list in criteria_dict.items():
            if not criteria_list:
                continue
            criteria_text = "\n".join(criteria_list) + "\n"
            topic_section = "\n".join(topic.get(get_topic_key(criteria_type), []))
            prompt_text = f"{prompt_base}{criteria_text}\nPatient Characteristics (DO NOT LABEL):\n{topic_section}"
            labels[criteria_type] = prompt_model(prompt_text, model, provider=current_provider, api_key=current_api_key)
        return labels

    inclusion_labels = process_criteria(inclusion_dict, inclusion_prompt_base)
    exclusion_labels = process_criteria(exclusion_dict, exclusion_prompt_base)

    return {"inclusion": inclusion_labels, "exclusion": exclusion_labels}


def parse_output(text):
    """
    Parses a string containing multiple JSON objects (one per line) and returns a list of parsed dictionaries.
    """
    items = []
    for line in text.strip().splitlines():
        line = line.strip()
        if line.startswith("Output:"):
            line = line[len("Output:"):].strip()
            if not line:
                continue
        if line:
            try:
                item = json.loads(line)
                if isinstance(item, dict):
                    items.append(item)
            except json.JSONDecodeError:
                continue
    return items


def extract_categorised_criteria(trial):
    """
    Extracts categorised inclusion and exclusion criteria from a trial.
    """
    desired_keys = ["demographic criteria", "disease criteria", "prior treatment criteria"]
    inclusion = {key: [] for key in desired_keys}
    exclusion = {key: [] for key in desired_keys}

    # Process inclusion criteria.
    inclusion_text = trial.get("inclusion", "")
    for item in parse_output(inclusion_text):
        criterion = item.get("Criterion", "")
        for category in item.get("Category", []):
            cat_lower = category.lower()
            if cat_lower in inclusion:
                inclusion[cat_lower].append(criterion)

    # Process exclusion criteria.
    exclusion_text = trial.get("exclusion", "")
    for item in parse_output(exclusion_text):
        criterion = item.get("Criterion", "")
        for category in item.get("Category", []):
            cat_lower = category.lower()
            if cat_lower in exclusion:
                exclusion[cat_lower].append(criterion)

    return {"inclusion": inclusion, "exclusion": exclusion}


def extract_lists(text):
    """
    Extracts list values for each key from text that may be in a JSON-like format
    (with curly braces and square-bracketed lists) or in a bullet list format.
    """
    text = text.strip()
    if text.startswith("Output:"):
        text = text[len("Output:"):].strip()

    # Attempt JSON-like extraction if curly braces are present.
    if "{" in text:
        if text.count("{") > text.count("}"):
            text += "}"
        pattern = r'["]?([^":\n]+)["]?\s*:\s*\[(.*?)\](?:,|\n|$)'
        matches = re.findall(pattern, text, re.DOTALL)
        if matches:
            result = {}
            for key, list_text in matches:
                if '-' in list_text:
                    items = re.findall(r'-\s*(.*)', list_text)
                else:
                    items = []
                    for quoted, unquoted in re.findall(r'"(.*?)"|([^,\n]+)', list_text):
                        item = quoted if quoted else unquoted
                        item = item.strip().strip('"')
                        if item:
                            items.append(item)
                result[key.strip()] = items
            if result:
                return result

    # Fallback: parse as bullet list format.
    result = {}
    current_key = None
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        key_match = re.match(r'^["]?([^":]+)["]?:\s*$', line)
        if key_match:
            current_key = key_match.group(1).strip()
            result[current_key] = []
        elif current_key is not None:
            bullet_match = re.match(r'^[-\*]\s*(.*)', line)
            if bullet_match:
                result[current_key].append(bullet_match.group(1).strip())
            else:
                if result[current_key]:
                    result[current_key][-1] += " " + line
                else:
                    result[current_key].append(line)
    return result


def extract_categorised_topics(processed_topics):
    """
    Extracts and normalizes categorised topics from processed topics.
    """
    topic_keys = ["demographic characteristics", "disease characteristics", "prior treatment"]
    categorised_topics = {}
    for topic_id, text in processed_topics.items():
        json_obj = extract_lists(text)
        normalized = {key: {} for key in topic_keys}
        for key, value in json_obj.items():
            normalized_key = key.strip().lower()
            normalized[normalized_key] = value
        categorised_topics[topic_id] = normalized
    return categorised_topics
