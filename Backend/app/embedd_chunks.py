from sentence_transformers import SentenceTransformer
import numpy as np

def embedd_chunks(chunks):
    model = SentenceTransformer('all-mpnet-base-v2')
    
    new_chunks = []

    for chunk in chunks:
        embeddings = model.encode(chunk, convert_to_numpy=True)
        new_chunks.append(embeddings)
        
    return new_chunks