# 🏥 Controlled LLM-based reasoning for clinical trial retrieval

---

## 📋 Table of Contents

- [Features](#-features)
- [Installation](#-installation)
- [Dataset Access](#-dataset-access)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [Project Structure](#-project-structure)
- [Model API](#-model-api)
- [Evaluation](#-evaluation)
- [Citation](#-citation)

---

## 🛠️ Installation

### 1. Clone this repo
```bash
git clone https://github.com/Mael7307/Controlled-LLM-based-Reasoning-for-Clinical-Trial-Retrieval.git
cd Controlled-LLM-based-Reasoning-for-Clinical-Trial-Retrieval
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set up pymedtermino2

The system uses pymedtermino2 for SNOMED-CT ontology access. For detailed setup instructions, please refer to:

→ https://owlready2.readthedocs.io/en/latest/pymedtermino2.html

After following the setup guide, initialize the SNOMED-CT ontology:

```bash
python -c "from src.utils.init_snomed_ontology import *"
```

---

## 🔑 Dataset Access

### 📌 ClinicalTrials.gov Snapshot

The ClinicalTrials.gov XML snapshot cannot be distributed with this repository. To access the data:

→ https://www.trec-cds.org/2022.html

Once downloaded, place the ClinicalTrials.gov XML files in:
```
data/raw/ClinicalTrials.2021-04-27/
```

### 📌 TREC 2022 Data

The TREC 2022 Clinical Trials Track topics and qrels should be placed in `data/raw/`:
- `topics2022.xml` - Topic descriptions
- `TREC_2022_qrels.txt` - Gold Relevance judgments

### 📌 UMLS/SNOMED-CT Data

Place the UMLS data file in `data/raw/`:
- `umls-2024AB-full.zip` - UMLS full release (or your version)

---

## ⚙️ Configuration

The system can be configured using environment variables or by modifying `src/utils/config.py`:

### Environment Variables

- `MODEL_PROVIDER`: Model provider to use (`"ollama"` or `"openai"`, default: `"ollama"`)
- `MODEL_NAME`: Model name (e.g., `"qwen2"` for Ollama, `"gpt-4"` or `"gpt-3.5-turbo"` for OpenAI)
- `OPENAI_API_KEY`: OpenAI API key (required if using OpenAI provider)

### Example Configuration

**For Ollama:**
```bash
export MODEL_PROVIDER=ollama
export MODEL_NAME=qwen2
```

**For OpenAI:**
```bash
export MODEL_PROVIDER=openai
export MODEL_NAME=gpt-4
export OPENAI_API_KEY=your-api-key-here
```

---

## 🚀 Usage

The system follows a pipeline-based approach. Run scripts in the `scripts/` directory in order:

### 1️⃣ Process Topics
```bash
python scripts/run_process_topics.py
```

### 2️⃣ Build SNOMED-CT Index
```bash
python scripts/run_snomed_lsh_index.py
```

### 3️⃣ Build Target Conditions
```bash
python scripts/run_build_target_conditions.py
```

### 4️⃣ Map Conditions
```bash
python scripts/run_map_conditions.py
```

### 5️⃣ Map Diagnoses
```bash
python scripts/run_map_diagnoses.py
```

### 6️⃣ Initial Retrieval
```bash
python scripts/run_initial_retrieval.py
```

### 7️⃣ Process Trials
```bash
python scripts/run_processs_trials.py
```

### 8️⃣ Coarse Labelling
```bash
python scripts/run_coarse_labelling.py
```

### 9️⃣ Fine-Grained Labelling
```bash
python scripts/run_fine_grained_labelling.py
```

### 🔟 Re-ranking and Evaluation
```bash
python scripts/run_re_ranking.py
```

---

## 📁 Project Structure

```
OntoTrial/
├── data/
│   ├── raw/                  # Raw data files (UMLS, ClinicalTrials XML, etc.)
│   ├── processed/            # Processed data (indices, mapped conditions, etc.)
│   └── prompts/              # Prompt templates for LLM processing
├── results/                  # Output results and evaluations
├── scripts/                  # Execution scripts for each pipeline stage
│   ├── run_process_topics.py
│   ├── run_snomed_lsh_index.py
│   ├── run_build_target_conditions.py
│   ├── run_map_conditions.py
│   ├── run_map_diagnoses.py
│   ├── run_initial_retrieval.py
│   ├── run_processs_trials.py
│   ├── run_coarse_labelling.py
│   ├── run_fine_grained_labelling.py
│   └── run_re_ranking.py
├── src/
│   ├── build_SNOMED/         # SNOMED-CT indexing and LSH implementation
│   ├── processing/           # Main processing modules (labelling, ranking, etc.)
│   └── utils/                # Utility modules (config, evaluation, APIs, etc.)
└── requirements.txt          # Python dependencies
```

---

## 🤖 Model API

The system supports multiple LLM providers through a unified API interface:

### Using Ollama (Local Models)

```python
from src.utils.model_api import prompt_model

response = prompt_model(
    prompt="Your prompt here",
    model="qwen2",
    provider="ollama"
)
```

### Using OpenAI

```python
from src.utils.model_api import prompt_model

response = prompt_model(
    prompt="Your prompt here",
    model="gpt-4",
    provider="openai",
    api_key="your-api-key"  # Optional if OPENAI_API_KEY env var is set
)
```

---

## 📊 Evaluation

The system uses `trectools` for evaluation and produces standard IR metrics:

- **NDCG@10**: Normalized Discounted Cumulative Gain at rank 10
- **Precision@10, Precision@25**: Precision at different cutoffs
- **MAP**: Mean Average Precision
- **R-Precision**: Precision at R relevant documents
- **Bpref**: Binary preference measure
- **MRR**: Mean Reciprocal Rank

Results are saved in the `results/` directory with standard TREC formatting.

---

## 📄 Citation

If you use this code in your research, please cite:

```bibtex
@article{jullien2024controlled,
  title={Controlled LLM-based reasoning for clinical trial retrieval},
  author={Jullien, Mael and Bogatu, Alex and Unsworth, Harriet and Freitas, Andre},
  journal={arXiv preprint arXiv:2409.18998},
  year={2024}
}
```

