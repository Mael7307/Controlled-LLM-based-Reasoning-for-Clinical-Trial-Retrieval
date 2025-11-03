import os

# Define the base directory (assumes this file is in src/)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
DATA_DIR = os.path.join(BASE_DIR, "data")
RAW_DIR = os.path.join(DATA_DIR, "raw")
PROCESSED_DIR = os.path.join(DATA_DIR, "processed")
PROMPT_DIR = os.path.join(DATA_DIR, "prompts")

# RUN SETTINGS
# Model provider: "ollama" or "openai"
MODEL_PROVIDER = os.getenv("MODEL_PROVIDER", "ollama")
# Model name (e.g., "qwen2" for Ollama, "gpt-4" or "gpt-3.5-turbo" for OpenAI)
MODEL_NAME = os.getenv("MODEL_NAME", "qwen2")
# OpenAI API key (optional, can also be set via OPENAI_API_KEY env var)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", None)

# Backward compatibility
OLLAMA_MODEL = MODEL_NAME

RUN_NAME = "run1"
RESULTS_DIR = os.path.join(BASE_DIR, "results", MODEL_NAME, RUN_NAME)
DEPTH = 1
INITIAL_RETRIEVAL_DIR = os.path.join(RESULTS_DIR, "filtered_retrieval")

# File paths for Step 1: Topic Modeling
TOPIC_PROMPT_PATH = os.path.join(PROMPT_DIR, "topic_prompt.txt")
TOPICS_XML_PATH = os.path.join(RAW_DIR, "topics2022.xml")

# File paths for Step 2: SNOMED-CT Indexing
SNOMED_PATH = os.path.join(RAW_DIR, "snomed_dict.json")
SNOMED_INDEX_PATH = os.path.join(PROCESSED_DIR, "lsh_index.pkl")

# File paths for Step 3: Clinical Trials Indexing
TRIALS_XML_DIR= os.path.join(RAW_DIR, "ClinicalTrials.2021-04-27")
CONDITIONS_JSON_PATH = os.path.join(PROCESSED_DIR, "conditions.json")

# File paths for Step 4: Mapping CT Conditions to SNOMED-CT
LSH_INDEX_PATH = os.path.join(PROCESSED_DIR, "lsh_index.pkl")
MAPPED_CONDITIONS_PATH = os.path.join(PROCESSED_DIR, "mapped_conditions.json")

# File paths for Step 5: Mapping Topics Diagnoses to SNOMED-CT
MAPPED_DIAGNOSES_PATH = os.path.join(RESULTS_DIR, "mapped_diagnoses.json")
PROCESSED_TOPICS_PATH = os.path.join(RESULTS_DIR, "processed_topics.json")

# File paths for Step 6: Initial Retrieval
TREC_QRELS_PATH = os.path.join(RAW_DIR, "TREC_2022_qrels.txt")
TOPIC_DIR = os.path.join(PROCESSED_DIR, "topic_descriptions.json")
STRUCTURED_TOPIC_DIR = os.path.join(RESULTS_DIR, "processed_topics.json")

# File paths for Step 7: Trial Structuring
TOP_N = 50

# File paths for Step 7: Coarse Labelling

# File paths for Step 8: Fine Labelling

