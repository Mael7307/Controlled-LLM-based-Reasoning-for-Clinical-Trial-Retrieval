import re
import os
from src.utils.json import *
from .trials import extract_top_trials
from src.utils.evaluation import save_results_and_evaluate


def filtered_inclusion_eligibility(fine_labels, initial_retrieval):
    results = {}
    for topic, trials in fine_labels.items():
        ordered_trials = initial_retrieval.get(topic, [])
        trial_ids = []
        eligibility_scores = []
        for trial_id, trial_data in trials.items():
            eligible_count = 0
            excluded_count = 0
            total_count = 0
            inclusion = trial_data.get('inclusion', {})
            if not inclusion:
                continue
            for criterion, crit_data in inclusion.items():
                eligible_count += crit_data["eligible"]
                excluded_count += crit_data["excluded"]
                total_count += crit_data["total"]
            if excluded_count > 0:
                score = 0
            else:
                score = eligible_count / total_count if total_count > 0 else 0
            trial_ids.append(trial_id)
            eligibility_scores.append(score)

        # When scores are equal, we want the trial that appears earlier in `ordered_trials` (i.e., lower index) to come first.
        # To do that, we use the negative index (since lower index gives a higher value when negated).
        sorted_pairs = sorted(
            zip(trial_ids, eligibility_scores),
            key=lambda pair: (
                pair[1],
                -ordered_trials.index(pair[0])
            ),
            reverse=True
        )
        if sorted_pairs:
            sorted_trial_ids, sorted_scores = zip(*sorted_pairs)
            trial_ids, eligibility_scores = list(sorted_trial_ids), list(sorted_scores)
        else:
            trial_ids, eligibility_scores = [], []

        results[topic] = (trial_ids, eligibility_scores)
    return results


def inclusion_eligibility(fine_labels, initial_retrieval):
    results = {}
    for topic, trials in fine_labels.items():
        ordered_trials = initial_retrieval.get(topic, [])
        trial_ids = []
        eligibility_scores = []
        for trial_id, trial_data in trials.items():
            eligible_count = 0
            total_count = 0
            inclusion = trial_data.get('inclusion', {})
            if not inclusion:
                continue
            for criterion, crit_data in inclusion.items():
                eligible_count += crit_data["eligible"]
                total_count += crit_data["total"]
            score = eligible_count / total_count if total_count > 0 else 0
            trial_ids.append(trial_id)
            eligibility_scores.append(score)

        sorted_pairs = sorted(
            zip(trial_ids, eligibility_scores),
            key=lambda pair: (
                pair[1],
                -ordered_trials.index(pair[0])
            ),
            reverse=True
        )
        if sorted_pairs:
            sorted_trial_ids, sorted_scores = zip(*sorted_pairs)
            trial_ids, eligibility_scores = list(sorted_trial_ids), list(sorted_scores)
        else:
            trial_ids, eligibility_scores = [], []

        results[topic] = (trial_ids, eligibility_scores)
    return results


def exclusion_eligibility(fine_labels, initial_retrieval):
    results = {}
    for topic, trials in fine_labels.items():
        ordered_trials = initial_retrieval.get(topic, [])
        trial_ids = []
        eligibility_scores = []
        for trial_id, trial_data in trials.items():
            eligible_count = 0
            total_count = 0
            exclusion = trial_data.get('exclusion', {})
            if not exclusion:
                continue
            for criterion, crit_data in exclusion.items():
                eligible_count += crit_data["eligible"]
                total_count += crit_data["total"]
            score = eligible_count / total_count if total_count > 0 else 0
            trial_ids.append(trial_id)
            eligibility_scores.append(score)

        sorted_pairs = sorted(
            zip(trial_ids, eligibility_scores),
            key=lambda pair: (
                pair[1],
                -ordered_trials.index(pair[0])
            ),
            reverse=True
        )
        if sorted_pairs:
            sorted_trial_ids, sorted_scores = zip(*sorted_pairs)
            trial_ids, eligibility_scores = list(sorted_trial_ids), list(sorted_scores)
        else:
            trial_ids, eligibility_scores = [], []

        results[topic] = (trial_ids, eligibility_scores)
    return results


def general_eligibility(fine_labels, initial_retrieval):
    results = {}
    for topic, trials in fine_labels.items():
        ordered_trials = initial_retrieval.get(topic, [])
        trial_ids = []
        eligibility_scores = []
        for trial_id, trial_data in trials.items():
            eligible_count = 0
            total_count = 0
            for section in ['inclusion', 'exclusion']:
                criteria_dict = trial_data.get(section, {})
                if not criteria_dict:
                    continue
                for crit_type, crit_data in criteria_dict.items():
                    eligible_count += crit_data["eligible"]
                    total_count += crit_data["total"]

            score = eligible_count / total_count if total_count > 0 else 0
            trial_ids.append(trial_id)
            eligibility_scores.append(score)

        sorted_pairs = sorted(
            zip(trial_ids, eligibility_scores),
            key=lambda pair: (
                pair[1],
                -ordered_trials.index(pair[0])
            ),
            reverse=True
        )
        if sorted_pairs:
            sorted_trial_ids, sorted_scores = zip(*sorted_pairs)
            trial_ids, eligibility_scores = list(sorted_trial_ids), list(sorted_scores)
        else:
            trial_ids, eligibility_scores = [], []

        results[topic] = (trial_ids, eligibility_scores)
    return results


def contrasting_eligibility(fine_labels, initial_retrieval):
    results = {}
    for topic, trials in fine_labels.items():
        ordered_trials = initial_retrieval.get(topic, [])
        trial_ids = []
        eligibility_scores = []
        for trial_id, trial_data in trials.items():
            eligible_count = 0
            excluded_count = 0
            total_count = 0
            for section in ['inclusion', 'exclusion']:
                criteria_dict = trial_data.get(section, {})
                if not criteria_dict:
                    continue
                for crit_type, crit_data in criteria_dict.items():
                    eligible_count += crit_data["eligible"]
                    excluded_count += crit_data["excluded"]
                    total_count += crit_data["total"]

            score = (eligible_count - excluded_count)/ total_count if total_count > 0 else 0
            trial_ids.append(trial_id)
            eligibility_scores.append(score)

        sorted_pairs = sorted(
            zip(trial_ids, eligibility_scores),
            key=lambda pair: (
                pair[1],
                -ordered_trials.index(pair[0])
            ),
            reverse=True
        )
        if sorted_pairs:
            sorted_trial_ids, sorted_scores = zip(*sorted_pairs)
            trial_ids, eligibility_scores = list(sorted_trial_ids), list(sorted_scores)
        else:
            trial_ids, eligibility_scores = [], []

        results[topic] = (trial_ids, eligibility_scores)
    return results


def coarse_grained_eligibility(coarse_labels, initial_retrieval):
    results = {}
    for topic, trials in coarse_labels.items():
        ordered_trials = initial_retrieval.get(topic, [])
        trial_ids = []
        eligibility_scores = []
        for trial_id, trial_data in trials.items():
            if trial_data == "eligible":
                score = 1
            else:
                score = 0
            trial_ids.append(trial_id)
            eligibility_scores.append(score)

        sorted_pairs = sorted(
            zip(trial_ids, eligibility_scores),
            key=lambda pair: (
                pair[1],
                -ordered_trials.index(pair[0])
            ),
            reverse=True
        )
        if sorted_pairs:
            sorted_trial_ids, sorted_scores = zip(*sorted_pairs)
            trial_ids, eligibility_scores = list(sorted_trial_ids), list(sorted_scores)
        else:
            trial_ids, eligibility_scores = [], []

        results[topic] = (trial_ids, eligibility_scores)
    return results


def hybrid_eligibility(fine_labels, coarse_labels, initial_retrieval):
    results = {}
    for topic, trials in fine_labels.items():
        ordered_trials = initial_retrieval.get(topic, [])
        trial_ids = []
        eligibility_scores = []
        for trial_id, trial_data in trials.items():
            coarse_score = 1 if coarse_labels[topic][trial_id] == "eligible" else 0
            eligible_count = 0
            excluded_count = 0
            total_count = 0
            for section in ['inclusion', 'exclusion']:
                criteria_dict = trial_data.get(section, {})
                if not criteria_dict:
                    continue
                for crit_type, crit_data in criteria_dict.items():
                    eligible_count += crit_data["eligible"]
                    excluded_count += crit_data["excluded"]
                    total_count += crit_data["total"]
            fine_score = eligible_count / total_count if total_count > 0 else 0
            score = coarse_score + fine_score
            trial_ids.append(trial_id)
            eligibility_scores.append(score)

        sorted_pairs = sorted(
            zip(trial_ids, eligibility_scores),
            key=lambda pair: (
                pair[1],
                -ordered_trials.index(pair[0])
            ),
            reverse=True
        )
        if sorted_pairs:
            sorted_trial_ids, sorted_scores = zip(*sorted_pairs)
            trial_ids, eligibility_scores = list(sorted_trial_ids), list(sorted_scores)
        else:
            trial_ids, eligibility_scores = [], []

        results[topic] = (trial_ids, eligibility_scores)
    return results


def single_criteria_eligibility(fine_labels, initial_retrieval, criteria_type):
    results = {}
    for topic, trials in fine_labels.items():
        ordered_trials = initial_retrieval.get(topic, [])
        trial_ids = []
        eligibility_scores = []
        for trial_id, trial_data in trials.items():
            eligible_count = 0
            total_count = 0
            inclusion = trial_data.get('inclusion', {})
            if not inclusion:
                continue
            crit_data = inclusion.get(criteria_type, {})
            if not crit_data:
                continue
            eligible_count += crit_data["eligible"]
            total_count += crit_data["total"]
            score = eligible_count / total_count if total_count > 0 else 0
            trial_ids.append(trial_id)
            eligibility_scores.append(score)

        sorted_pairs = sorted(
            zip(trial_ids, eligibility_scores),
            key=lambda pair: (
                pair[1],
                -ordered_trials.index(pair[0])
            ),
            reverse=True
        )
        if sorted_pairs:
            sorted_trial_ids, sorted_scores = zip(*sorted_pairs)
            trial_ids, eligibility_scores = list(sorted_trial_ids), list(sorted_scores)
        else:
            trial_ids, eligibility_scores = [], []

        results[topic] = (trial_ids, eligibility_scores)
    return results


## Label processing functions

def process_criteria_str(crit_str):
    """Process a criteria string and count eligible/excluded labels."""
    eligible_count = 0
    excluded_count = 0
    no_information_count = 0
    # Each line is expected to represent a separate criteria item
    for line in crit_str.splitlines():
        line = line.strip()
        if not line:
            continue
        if re.search(r"""['"]Label['"]\s*:\s*['"]eligible['"]""", line):
            eligible_count += 1
        if re.search(r"""['"]Label['"]\s*:\s*['"]excluded['"]""", line):
            excluded_count += 1
        if re.search(r"""['"]Label['"]\s*:\s*['"]no relevant information['"]""", line):
            no_information_count += 1

    total = eligible_count + excluded_count + no_information_count
    return {"eligible": eligible_count, "excluded": excluded_count, "no_information": no_information_count, "total": total}

def process_fine_labels(data):
    """
    Process the nested trials dictionary so that for each trial and for each criteria type,
    we replace the string entry with a dict that counts 'eligible' and 'excluded' labels.
    """
    processed_data = {}
    for topic_id, trials in data.items():
        topic_dict = {}
        for trial_id, trial_data in trials.items():
            trial_dict = {}
            for section in ['inclusion', 'exclusion']:
                criteria_dict = trial_data.get(section, {})
                section_dict = {}
                for crit_type, crit_str in criteria_dict.items():
                    section_dict[crit_type] = process_criteria_str(crit_str)
                trial_dict[section] =section_dict
            topic_dict[trial_id] = trial_dict
        processed_data[topic_id] = topic_dict
    return processed_data

def process_trial_text(text):
    """
    Extract all label values from the text using a regex.
    Then decide on a final label:
    - If any label is 'excluded' or 'not eligible', return 'excluded'.
    - Otherwise, if at least one label is found, return 'eligible'.
    - If no labels are found, default to 'excluded'.
    """
    # Look for patterns like: "Output: {'label': 'eligible'}" or similar
    labels = re.findall(r"""['"]label['"]\s*:\s*['"](.*?)['"]""", text)

    # If no explicit output dictionary was found, use a fallback check
    if not labels:
        lower_text = text.lower()
        # Check if any of these substrings exist in the text
        if "eligible" in lower_text:
            labels.append("eligible")
        elif "excluded" in lower_text or "not eligible" in lower_text:
            labels.append("excluded")

    # Normalize labels for comparison
    normalized = [lab.strip().lower() for lab in labels]

    # If any of the labels is explicitly negative, return 'excluded'
    for lab in normalized:
        if lab in ["excluded", "not eligible"]:
            return "excluded"

    # If we have any positive labels and none are negative, return 'eligible'
    if normalized:
        return "eligible"

    # Fallback default if no decision could be made
    return "excluded"

def process_coarse_labels(data):
    """
    Process the nested trials dictionary.
    For each trial entry, replace the trial text
    with a final decision: 'eligible' or 'excluded'.
    """
    new_data = {}
    for group, trials in data.items():
        new_trials = {}
        for trial_id, trial_text in trials.items():
            new_trials[trial_id] = process_trial_text(trial_text)
        new_data[group] = new_trials
    return new_data


def re_ranking_and_evaluation(results_path, qrel_file):
    qrel_results_path = os.path.join(results_path,"filtered_retrieval", "qrel.txt")
    fine_grained_label_path = os.path.join(results_path, "fine_labelling.json")
    coarse_labels_path = os.path.join(results_path, "coarse_labelling.json")
    fine_labels = load_json(fine_grained_label_path)
    coarse_labels = load_json(coarse_labels_path)

    # Load Data
    qrel_results, _ = extract_top_trials(qrel_results_path, 50)
    processed_fine_labels = process_fine_labels(fine_labels)
    processed_coarse_labels = process_coarse_labels(coarse_labels)

    # Reranking
    filtered_inclusion_results = filtered_inclusion_eligibility(processed_fine_labels, qrel_results)
    inclusion_results = inclusion_eligibility(processed_fine_labels, qrel_results)
    exclusion_results = exclusion_eligibility(processed_fine_labels, qrel_results)
    general_results = general_eligibility(processed_fine_labels, qrel_results)
    contrasting_results = contrasting_eligibility(processed_fine_labels, qrel_results)
    coarse_results = coarse_grained_eligibility(processed_coarse_labels, qrel_results)
    hybrid_results = hybrid_eligibility(processed_fine_labels, processed_coarse_labels, qrel_results)
    demographic_results = single_criteria_eligibility(processed_fine_labels, qrel_results, "demographic criteria")
    disease_results = single_criteria_eligibility(processed_fine_labels, qrel_results, "disease criteria")
    treatment_results = single_criteria_eligibility(processed_fine_labels, qrel_results, "prior treatment criteria")

    # Save and Evaluate
    save_results_and_evaluate(filtered_inclusion_results, "filtered_inclusion", results_path, qrel_file)
    save_results_and_evaluate(inclusion_results, "inclusion", results_path, qrel_file)
    save_results_and_evaluate(exclusion_results, "exclusion", results_path, qrel_file)
    save_results_and_evaluate(general_results, "general", results_path, qrel_file)
    save_results_and_evaluate(contrasting_results, "contrasting", results_path, qrel_file)
    save_results_and_evaluate(coarse_results, "coarse", results_path, qrel_file)
    save_results_and_evaluate(hybrid_results, "hybrid", results_path, qrel_file)
    save_results_and_evaluate(demographic_results, "demographic", results_path, qrel_file)
    save_results_and_evaluate(disease_results, "disease", results_path, qrel_file)
    save_results_and_evaluate(treatment_results, "treatment", results_path, qrel_file)









