from .qgram_transformer import QGramTransformer
from .lsh_index import LSHIndex
from .hash_gen import *
import sys
sys.modules['lsh_index'] = sys.modules['src.build_SNOMED.lsh_index']
sys.modules['qgram_transformer'] = sys.modules['src.build_SNOMED.qgram_transformer']
sys.modules['hash_gen'] = sys.modules['src.build_SNOMED.hash_gen']
import pickle
from src.utils.json import load_json, save_json

def build_map(index_dir, conditions_dir, snomed_dict_dir, output_dir):
    conditions = load_json(conditions_dir)
    snomed_dict = load_json(snomed_dict_dir)
    print("Loading LSH index...")
    index = pickle.load(open(index_dir, 'rb'))

    qgram_transformer = QGramTransformer(qgram_size=3)

    # Default SNOMED fallback
    default_snomed = {'ID': '64572001', 'Snomed term': 'Disease'}

    # Dictionary to store results
    snomed_conditions = {}

    # Number of nearest neighbors
    k = 1
    with_scores = True

    # Total number of conditions
    total_conditions = len(conditions)

    # Process conditions with progress tracking
    for idx, (condition, associated_trials) in enumerate(conditions.items(), start=1):
        query_qgrams = qgram_transformer.transform(condition)
        results = index.query(query=query_qgrams, k=k, with_scores=with_scores)

        if results:
            top_match = results[0][0]  # Get top match ID
            snomed_conditions[condition] = {
                'ID': str(snomed_dict[top_match]['concept']),
                'Snomed term': snomed_dict[top_match]['term'],
                'Associated trials': associated_trials
            }
        else:
            snomed_conditions[condition] = {**default_snomed, 'Associated trials': associated_trials}

        # Print real-time progress
        progress = (idx / total_conditions) * 100
        print(f"Progress: {progress:.2f}% ({idx}/{total_conditions} conditions processed)", end="\r")

    print("\nProcessing complete.")

    # Save results
    save_json(snomed_conditions, output_dir)




