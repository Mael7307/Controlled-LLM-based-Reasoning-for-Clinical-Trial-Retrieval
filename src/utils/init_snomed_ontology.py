from owlready2.pymedtermino2.umls import *
from .config import BASE_DIR, RAW_DIR
import os

# Set the backend to store the ontology in a SQLite database
# Store the SQLite database in the utils directory
sqlite_path = os.path.join(BASE_DIR, "src", "utils", "pym.sqlite3")
default_world.set_backend(filename=sqlite_path)

# Use the UMLS zip file from the raw data directory
umls_zip_path = os.path.join(RAW_DIR, "umls-2024AB-full.zip")
if os.path.exists(umls_zip_path):
    import_umls(umls_zip_path, terminologies=["SNOMEDCT_US"])
    default_world.save()
else:
    raise FileNotFoundError(f"UMLS file not found at {umls_zip_path}. Please ensure the UMLS file is in the data/raw directory.")