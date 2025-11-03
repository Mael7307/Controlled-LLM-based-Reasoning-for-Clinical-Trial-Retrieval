from src.build_SNOMED.qgram_transformer import QGramTransformer
from src.build_SNOMED.lsh_index import LSHIndex
from src.build_SNOMED.hash_gen import *
import sys
sys.modules['lsh_index'] = sys.modules['src.build_SNOMED.lsh_index']
sys.modules['qgram_transformer'] = sys.modules['src.build_SNOMED.qgram_transformer']
sys.modules['hash_gen'] = sys.modules['src.build_SNOMED.hash_gen']
from src.utils.json import load_json, save_json
import pickle


def process_topic_output(data_str):
    """
    Extracts data from the text based on predefined topic keys.
    """
    keys = ["disease characteristics", "demographic characteristics", "prior treatment", "suggested diagnosis"]

    return {
        key: [
            value.strip() for value in
            data_str[data_str.find("[", pos) + 1: data_str.find("]", data_str.find("[", pos))].split(",")
        ] if pos != -1 else []
        for key, pos in ((k, data_str.find(k)) for k in keys)
    }

def diagnoses_map(index_dir, snomed_dict_dir, processed_topic_dir, output_dir, SNOMEDCT_US, show_avg_score=True):
    snomed_dict = load_json(snomed_dict_dir)
    processsed_topics = load_json(processed_topic_dir)
    print("Loading LSH index...")
    index = pickle.load(open(index_dir, "rb"))

    # Initialize QGram Transformer
    qgram_transformer = QGramTransformer(qgram_size=3)

    # Parameters
    k = 5  # Number of nearest neighbors
    with_scores = True  # Retrieve similarity scores

    extracted_diagnoses = {key : [] for key in processsed_topics.keys()}

    for topic_num, topic_data in processsed_topics.items():
        topic_data = process_topic_output(topic_data.lower())
        diagnosis = topic_data.get("suggested diagnosis", [])
        if diagnosis:
            extracted_diagnoses[topic_num] = diagnosis[0]
            print(extracted_diagnoses[topic_num])
        else:
            print(f"Warning: No diagnosis found in topic {topic_num}")
            extracted_diagnoses[topic_num] = []


    disease = SNOMEDCT_US[64572001]

    # Process diagnoses and map to SNOMED
    diag_dict = {}
    scores = []

    for key, diagnosis in extracted_diagnoses.items():
        diag_dict[key] = {}
        print(f"Querying for condition {key} of {len(extracted_diagnoses)}")

        query_qgrams = qgram_transformer.transform(diagnosis)
        results = index.query(query=query_qgrams, k=k, with_scores=with_scores)
        disease_diagnosis_found = False
        for result in results:
            uid = result[0]
            print(uid)

            if issubclass(SNOMEDCT_US[snomed_dict[uid]["concept"]], disease):
                diag_dict[key] = {
                    "diagnosis": diagnosis,
                    "snomed": snomed_dict[uid]["term"],
                    "snomed_id": snomed_dict[uid]["concept"],
                }
                scores.append(result[1])
                disease_diagnosis_found = True
                print(f"Found diseased {snomed_dict[uid]['term']} for diagnosis {diagnosis}")
                break

        if not disease_diagnosis_found:
            print("Using backup")
            top_match = results[0]
            scores.append(top_match[1])
            diag_dict[key] = {
                "diagnosis": diagnosis,
                "snomed": snomed_dict[top_match[0]]["term"],
                "snomed_id": snomed_dict[top_match[0]]["concept"],
            }


    if show_avg_score:
        print(f"Average score: {sum(scores) / len(scores):.4f}")

    save_json(diag_dict, output_dir)



