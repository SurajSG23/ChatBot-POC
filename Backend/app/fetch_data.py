from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import pickle
import os

def fetch_data(prompt,project):
    index_path = os.path.abspath(f"FAISS/{project}/faiss_index.index")

    index = faiss.read_index(index_path)
    # Load the original corpus used to build the index
    with open(f"FAISS/{project}/corpus.pkl", "rb") as f:
        corpus = pickle.load(f)

    # Load the sentence transformer model
    model = SentenceTransformer('all-mpnet-base-v2')

    # Encode the query
    query_vector = model.encode([prompt]).astype('float32')

    # Search the index
    k = 10
    distance, indices = index.search(query_vector, k)
    top_matches = []
    
    for idx in indices[0]:
        top_matches.append(corpus[idx].split(",")[0].split(":")[1].strip())
        
    return top_matches