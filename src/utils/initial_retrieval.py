from .SNOMED_retrieval import retrieve_relevant_trials
from .BM25 import bm25_rank_documents
from .evaluation import save_results_and_evaluate
from .demographics import filter_trials_by_demographics

def run_initial_retrieval(
    diagnoses_mapping_path, conditions_mapping_path, retrieval_depth, qrels_path,
    trials_xml_directory, topic_directory, SNOMEDCT_US, results_directory, structured_topics_dir):
    """
    Executes the initial retrieval pipeline, including SNOMED-based relevance retrieval
    and BM25 ranking, followed by result saving and evaluation.
    """

    # Perform SNOMED-based relevance retrieval
    relevant_trials = retrieve_relevant_trials(
        diagnoses_mapping_path, conditions_mapping_path, qrels_path, SNOMEDCT_US)

    # Rank retrieved trials using BM25
    ranked_trials = bm25_rank_documents(relevant_trials, trials_xml_directory, topic_directory)

    # Save ranked results and evaluate performance
    save_results_and_evaluate(ranked_trials, 'ranked_retrieval', results_directory, qrels_path)

    filtered_trials = filter_trials_by_demographics(ranked_trials, structured_topics_dir, trials_xml_directory)

    # Save filtered results and evaluate performance
    save_results_and_evaluate(filtered_trials, 'filtered_retrieval', results_directory, qrels_path)

    return
