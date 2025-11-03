import os
import re
from typing import Any, Dict, List, Optional, Tuple
from .xml_parsing import xml_processing
from .json import load_json


def extract_trial_conditions(trial_id: str, base_path: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """
    Extracts gender, minimum_age, and maximum_age from a clinical trial's XML file.

    :param trial_id: The clinical trial identifier.
    :param base_path: The directory path where the XML file is located.
    :return: A tuple (gender, minimum_age, maximum_age) as extracted from the file.
    """
    file_path = os.path.join(base_path, f'{trial_id}.xml')
    extracted_data = xml_processing(file_path)
    trial_info = extracted_data[2]
    gender = trial_info.get('gender')
    minimum_age = trial_info.get('minimum_age')
    maximum_age = trial_info.get('maximum_age')
    return gender, minimum_age, maximum_age


def parse_structured_topic(topic_str: str) -> Dict[str, List[str]]:
    """
    Parses a structured topic string to extract values for predefined keys.
    Expected keys include:
      - "disease characteristics"
      - "demographic characteristics"
      - "prior treatment"
      - "suggested diagnosis"

    Each key should be followed by a comma-separated list enclosed in square brackets.

    :param topic_str: The structured topic string.
    :return: A dictionary mapping each key to a list of extracted values.
    """
    keys = [
        "disease characteristics",
        "demographic characteristics",
        "prior treatment",
        "suggested diagnosis"
    ]
    topic_str_lower = topic_str.lower()
    result = {}

    for key in keys:
        start = topic_str_lower.find(key)
        if start != -1:
            bracket_start = topic_str_lower.find('[', start)
            bracket_end = topic_str_lower.find(']', bracket_start)
            if bracket_start != -1 and bracket_end != -1:
                values_str = topic_str_lower[bracket_start + 1:bracket_end]
                values = [value.strip() for value in values_str.split(',') if value.strip()]
                result[key] = values
            else:
                result[key] = []
        else:
            result[key] = []

    return result


def extract_topics_demographics(json_path: str) -> Dict[str, List[str]]:
    """
    Extracts demographic characteristics for each topic from a JSON file.

    :param json_path: Path to the JSON file containing topics.
    :return: A dictionary mapping topic IDs to their list of demographic characteristics.
    """
    topics_dict = load_json(json_path)
    demographics = {}
    for topic_id, topic_text in topics_dict.items():
        structured_topic = parse_structured_topic(topic_text)
        demo_chars = structured_topic.get('demographic characteristics', [])
        if not demo_chars:
            print(f'No demographic characteristics for topic {topic_id}')
        demographics[topic_id] = demo_chars
    return demographics


def is_age_within_range(patient_age: Optional[int],
                        patient_unit: Optional[str],
                        min_age: int,
                        max_age: int,
                        min_unit: str,
                        max_unit: str) -> bool:
    """
    Checks if the patient's age (after converting to years) falls within the provided range.
    Conversion factors are used to normalize values to years.

    :param patient_age: The patient's age.
    :param patient_unit: The unit of the patient's age.
    :param min_age: The minimum age requirement.
    :param max_age: The maximum age requirement.
    :param min_unit: The unit for the minimum age.
    :param max_unit: The unit for the maximum age.
    :return: True if the patient's age is within the specified range; otherwise, False.
    """
    if patient_age is None:
        return True

    # Default units to 'year' if not provided
    patient_unit = patient_unit or 'year'
    min_unit = min_unit or 'year'
    max_unit = max_unit or 'year'
    if not min_age:
        min_age = 0
        min_unit = 'year'
    if not max_age:
        max_age = 1000
        max_unit = 'year'

    conversion_factors = {
        'day': 1 / 365,
        'week': 1 / 52,
        'month': 1 / 12,
        'year': 1,
    }

    patient_age_years = patient_age * conversion_factors.get(patient_unit, 1)
    min_age_years = min_age * conversion_factors.get(min_unit, 1)
    max_age_years = max_age * conversion_factors.get(max_unit, 1)

    return min_age_years <= patient_age_years <= max_age_years


def parse_age_and_unit(age_str: str) -> Tuple[Optional[int], Optional[str]]:
    """
    Parses an age string to extract the first integer (age) and its corresponding unit.
    Units are normalized to singular form (e.g., 'years' -> 'year').

    :param age_str: The string containing the age and its unit.
    :return: A tuple (age, unit) or (None, None) if no valid age is found.
    """
    numbers = re.findall(r'\d+', age_str)
    age = int(numbers[0]) if numbers else None
    pattern = r'\b(?:year|month|week|day)s?\b'
    unit_match = re.search(pattern, age_str, flags=re.IGNORECASE)
    unit = unit_match.group(0).lower().rstrip('s') if unit_match else None
    return age, unit


def evaluate_demographic_relevance(
    min_age_str: Optional[str],
    max_age_str: Optional[str],
    trial_gender: Optional[str],
    patient_demographics: List[str]
) -> Tuple[bool, bool]:
    """
    Evaluates whether the patient's demographics are relevant with respect to the trial's
    age and gender requirements.

    :param min_age_str: The trial's minimum age requirement as a string.
    :param max_age_str: The trial's maximum age requirement as a string.
    :param trial_gender: The trial's gender requirement (defaults to 'all' if unspecified).
    :param patient_demographics: A list of strings representing the patient's demographic info.
    :return: A tuple (age_relevance, gender_relevance).
    """
    trial_gender = trial_gender or 'all'

    if min_age_str:
        min_age, min_unit = parse_age_and_unit(min_age_str)
    else:
        min_age, min_unit = 0, 'year'

    if max_age_str:
        max_age, max_unit = parse_age_and_unit(max_age_str)
    else:
        max_age, max_unit = 1000, 'year'

    patient_age: Optional[int] = None
    patient_unit: Optional[str] = None
    patient_gender: Optional[str] = None
    found_age = False
    found_gender = False
    gender_keywords = ['male', 'female', 'all']

    for demo in patient_demographics:
        demo_lower = demo.lower()
        if 'age' in demo_lower and 'mother' not in demo_lower:
            found_age = True
            patient_age, patient_unit = parse_age_and_unit(demo_lower)
        if 'gender' in demo_lower:
            for keyword in gender_keywords:
                if keyword in demo_lower:
                    patient_gender = keyword
                    found_gender = True
                    break

    age_relevance = is_age_within_range(
        patient_age, patient_unit, min_age, max_age, min_unit, max_unit
    ) if found_age else True

    if found_gender:
        gender_relevance = (
            True if 'all' in trial_gender.lower() or (patient_gender and patient_gender in trial_gender.lower())
            else False
        )
    else:
        gender_relevance = True

    return age_relevance, gender_relevance


def filter_trials_by_demographics(
    unfiltered_trials: Dict[Any, Tuple[List[str], List[float]]],
    topics_json_path: str,
    trial_xml_base_path: str
) -> Dict[Any, Tuple[List[str], List[float]]]:
    """
    Filters clinical trial retrievals based on demographic relevance.
    For each topic, retrieves its demographic criteria and filters the trial list by
    evaluating age and gender compatibility.

    :param unfiltered_trials: Dictionary mapping topic IDs to tuples (trial_ids, scores).
    :param topics_json_path: Path to the JSON file containing topics information.
    :param trial_xml_base_path: Directory path where trial XML files are stored.
    :return: A dictionary with filtered trial IDs and scores for each topic.
    """
    topics_demographics = extract_topics_demographics(topics_json_path)
    filtered_trials = {}

    for topic_id, (trial_ids, scores) in unfiltered_trials.items():
        unfiltered_ttl = len(trial_ids)
        patient_demographics = topics_demographics.get(topic_id)
        filtered_trial_ids = []
        filtered_scores = []

        if patient_demographics:
            for trial_id, score in zip(trial_ids, scores):
                trial_gender, trial_min_age, trial_max_age = extract_trial_conditions(trial_id, trial_xml_base_path)
                age_ok, gender_ok = evaluate_demographic_relevance(
                    trial_min_age, trial_max_age, trial_gender, patient_demographics
                )
                if age_ok and gender_ok:
                    filtered_trial_ids.append(trial_id)
                    filtered_scores.append(score)
        else:
            filtered_trial_ids, filtered_scores = trial_ids, scores

        filtered_trials[topic_id] = (filtered_trial_ids, filtered_scores)
        print(f'Topic {topic_id}: {unfiltered_ttl} trials -> {len(filtered_trial_ids)} trials')

    return filtered_trials
