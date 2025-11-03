from .xml_parsing import *
from .json import *
import os
import re
from typing import Any, Dict, List, Optional, Tuple
from rank_bm25 import BM25Okapi
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
import nltk
nltk.download('stopwords')

# Preload common resources for text processing.
STOP_WORDS = set(stopwords.words('english'))
STEMMER = PorterStemmer()


def extract_xml_texts(xml_dir: str, xml_ids: List[str]) -> List[str]:

    extracted_texts = []
    for xml_id in xml_ids:
        # Build full file path and process the XML.
        file_path = os.path.join(xml_dir, f'{xml_id}.xml')
        inclusion_text, exclusion_text, element_dict = xml_processing(file_path)

        text_parts = []
        for key, value in element_dict.items():
            if value is not None:
                # For these keys, assume the value is a list.
                if key in ['condition', 'keyword', 'condition_browse']:
                    text_parts.append(' '.join(value))
                else:
                    text_parts.append(value)
        if inclusion_text is not None:
            text_parts.append(inclusion_text)
        if exclusion_text is not None:
            text_parts.append(exclusion_text)

        full_text = ' '.join(text_parts)
        extracted_texts.append(full_text)
    return extracted_texts


def preprocess_text(text: str) -> List[str]:
    """
    Preprocesses text by lowercasing, removing non-alphabetic characters,
    tokenizing, removing stopwords, and applying stemming.

    Parameters:
        text (str): The input text to preprocess.

    Returns:
        List[str]: A list of preprocessed tokens.
    """
    # Lowercase and remove non-alphabetic characters.
    text = text.lower()
    text = re.sub(r'[^a-zA-Z\s]', '', text)

    # Tokenize the text.
    tokens = word_tokenize(text)

    # Remove stopwords and stem the tokens.
    tokens = [STEMMER.stem(token) for token in tokens if token not in STOP_WORDS]

    return tokens


def retrieve_bm25_documents(query: str,
                            xml_dir: str,
                            xml_ids: List[str],
                            k1: float = 0.75,
                            b: float = 0.75) -> Tuple[List[str], List[float]]:
    """
    Ranks XML files using the BM25 algorithm based on the provided query.

    Parameters:
        query (Tuple[Any, str]): A tuple where the second element is the query text.
        xml_dir (str): Directory containing the XML files.
        xml_ids (List[str]): List of XML file identifiers.
        k1 (float): BM25 k1 parameter (default: 0.75).
        b (float): BM25 b parameter (default: 0.75).

    Returns:
        Tuple[List[str], List[float]]: A tuple containing the list of XML IDs ranked
        in descending order of BM25 score and their corresponding scores.
    """
    # Extract and preprocess text from the XML files.
    xml_texts = extract_xml_texts(xml_dir, xml_ids)
    tokenized_texts = [preprocess_text(text) for text in xml_texts]

    bm25_model = BM25Okapi(tokenized_texts, k1=k1, b=b)
    # The actual query text is the second element of the tuple.
    processed_query = preprocess_text(query)
    doc_scores = bm25_model.get_scores(processed_query)

    # Pair xml_id with its BM25 score, then sort in descending order.
    scored_results = sorted(zip(xml_ids, doc_scores), key=lambda pair: pair[1], reverse=True)
    ranked_ids, ranked_scores = zip(*scored_results) if scored_results else ([], [])

    return list(ranked_ids), list(ranked_scores)


def bm25_rank_documents(unranked_retrieval: Dict[str, List[str]],
                        xml_dir: str,
                        query_path: str):

    ranked_results: Dict[str, Tuple[List[str], List[float]]] = {}
    queries = load_json(query_path)

    for topic_index, xml_ids in unranked_retrieval.items():
        print(f"Ranking topic {topic_index}...")
        if not xml_ids:
            ranked_results[topic_index] = ([], [])
            continue
        topic_query = queries[topic_index]
        ranked_ids, ranked_scores = retrieve_bm25_documents(topic_query, xml_dir, xml_ids)
        ranked_scores = normalize_bm25_scores(ranked_scores)
        ranked_results[topic_index] = (ranked_ids, ranked_scores)
        print(f"Topic {topic_index}: {len(ranked_ids)} documents ranked.")
    return ranked_results


def normalize_bm25_scores(scores: List[float]) -> List[float]:
    """
    Normalizes a list of BM25 scores to the range [0, 2].

    Parameters:
        scores (List[float]): The BM25 scores to normalize.

    Returns:
        List[float]: Normalized BM25 scores in the range [0, 2].
    """
    if not scores:
        return []

    min_score = min(scores)
    max_score = max(scores)

    if max_score == min_score:
        return [1.0 for _ in scores]

    normalized = [
        2.0 * (score - min_score) / (max_score - min_score)
        for score in scores
    ]
    # Clamp values to the [0, 2] range.
    return [max(0.0, min(2.0, ns)) for ns in normalized]


# def generate_candidate_documents(topic_number: int,
#                                  qrels2022: List[List[Any]]) -> Tuple[List[str], List[List[Any]]]:
#
#     candidate_ids = []
#     candidate_qrels = []
#
#     for row in qrels2022:
#         if int(row[0]) == topic_number:
#             candidate_ids.append(row[2])
#             candidate_qrels.append(row)
#     return candidate_ids, candidate_qrels


# def filter_unique_bm25_documents(bm25_ids: List[str],
#                                  bm25_scores: List[float],
#                                  ranked_results: Dict[int, Tuple[List[str], List[float]]]) -> Tuple[List[str], List[float]]:
#     """
#     Filters BM25-retrieved documents to retain only those not already present
#     in the ranked retrieval results.
#
#     Parameters:
#         bm25_ids (List[str]): List of XML file identifiers retrieved via BM25.
#         bm25_scores (List[float]): Corresponding BM25 scores.
#         ranked_results (Dict[int, Tuple[List[str], List[float]]]): A dictionary of already ranked
#             documents (across all topics).
#
#     Returns:
#         Tuple[List[str], List[float]]: Unique XML file identifiers and their corresponding BM25 scores.
#     """
#     # Aggregate all previously ranked document identifiers.
#     existing_docs = set()
#     for docs, _ in ranked_results.values():
#         existing_docs.update(docs)
#
#     unique_ids = []
#     unique_scores = []
#     for doc_id, score in zip(bm25_ids, bm25_scores):
#         if doc_id not in existing_docs:
#             unique_ids.append(doc_id)
#             unique_scores.append(score)
#     return unique_ids, unique_scores
