from .qgram_transformer import QGramTransformer
from .lsh_index import LSHIndex
import os
import pickle
from src.utils.json_handler import load_json

def build_index(snomed_path, output_dir):
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Load SNOMED dictionary
    search_space = load_json(snomed_path)
    qgram_transformer = QGramTransformer(qgram_size=3)
    index = LSHIndex(256, similarity_threshold=0.3)

    for key, value in search_space.items():
        term = value["term"]
        term_id = value["id"]
        qgrams = qgram_transformer.transform(term)
        qgrams = qgrams + term.split()
        index.add(term_id, qgrams)

    with open(output_dir, "wb") as output_file:
        pickle.dump(index, output_file)
