from trectools import TrecQrel, TrecRun, TrecEval
import os
import numpy as np

def qrel_format(retrieval_results):
    q0 = 'Q0'
    run_name = 'my-run'
    results = []
    for key, value in retrieval_results.items():
        trial_list, score_list = value
        index = 1
        for trial, score in zip(trial_list, score_list):
            results_str = ' '.join([key, q0, trial, str(index), str(score), run_name])
            results.append(results_str)
            index += 1
    return results


def save_results_and_evaluate(retrieval_results, run_name, results_folder, qrel_file):
    folder_path = os.path.join(results_folder, run_name)
    qrel_path = os.path.join(folder_path, 'qrel.txt')
    results_path = os.path.join(folder_path,'results.txt')
    results = qrel_format(retrieval_results)
    # Save
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    with open(qrel_path, 'w') as file:
        for item in results:
            file.write("%s\n" % item)
    # Evaluate
    r1 = TrecRun(qrel_path)
    qrels = TrecQrel(qrel_file)
    data = TrecEval(r1, qrels)
    depth = 1000
    results_str = 'ndcg_10: ' + str(data.get_ndcg(depth=10, trec_eval=True)) + '\n'
    results_str += 'precision_10: ' + str(data.get_precision(depth=10, trec_eval=True)) + '\n'
    results_str += 'precision_25: ' + str(data.get_precision(depth=25, trec_eval=True)) + '\n'
    results_str += 'map: ' + str(data.get_map(depth=depth, trec_eval=True)) + '\n'
    results_str += 'rprec: ' + str(data.get_rprec(depth=depth, trec_eval=True)) + '\n'
    results_str += 'bpref: ' + str(data.get_bpref(depth=depth, trec_eval=True)) + '\n'
    results_str += 'MRR: ' + str(data.get_reciprocal_rank(depth=depth, trec_eval=True)) + '\n'
    print(results_str)
    with open(results_path, 'w') as file:
        file.write(results_str)
    return

def evaluate_qrel(qrel_results_path, qrel_file):
    r1 = TrecRun(qrel_results_path)
    qrels = TrecQrel(qrel_file)
    data = TrecEval(r1, qrels)
    depth = 1000
    results_str = 'ndcg_10: ' + str(data.get_ndcg(depth=10, trec_eval=True)) + '\n'
    results_str += 'precision_10: ' + str(data.get_precision(depth=10, trec_eval=True)) + '\n'
    results_str += 'precision_25: ' + str(data.get_precision(depth=25, trec_eval=True)) + '\n'
    results_str += 'map: ' + str(data.get_map(depth=depth, trec_eval=True)) + '\n'
    results_str += 'rprec: ' + str(data.get_rprec(depth=depth, trec_eval=True)) + '\n'
    results_str += 'bpref: ' + str(data.get_bpref(depth=depth, trec_eval=True)) + '\n'
    results_str += 'MRR: ' + str(data.get_reciprocal_rank(depth=depth, trec_eval=True)) + '\n'
    print(results_str)
    return
