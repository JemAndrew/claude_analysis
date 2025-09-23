# test_loading.py
from pathlib import Path
import sys
sys.path.append('src')

from utils import load_documents

docs = load_documents(Path('.'))
print(f"Loaded {len(docs)} documents")
for doc in docs[:3]:
    print(f"  - {doc['doc_id']}: {doc['text'][:50]}...")