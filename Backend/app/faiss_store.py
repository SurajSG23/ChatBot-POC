import faiss
import numpy as np
import os
import pickle

def faiss_store(chunks, original_texts, source):
    dimension = chunks[0].shape[0]
    vectors = np.array(chunks).astype('float32')

    index_path = os.path.join(source, "faiss_index.index")
    corpus_path = os.path.join(source, "corpus.pkl")

    os.makedirs(f"FAISS/{source}", exist_ok=True)

    if os.path.exists(f"FAISS/{index_path}") and os.path.exists(f"FAISS/{corpus_path}"):
        index = faiss.read_index(f"FAISS/{index_path}")

        with open(f"FAISS/{corpus_path}", "rb") as f:
            existing_texts = pickle.load(f)

        original_texts = existing_texts + original_texts
    else:
        
        index = faiss.IndexFlatL2(dimension)

    index.add(vectors) #type:ignore

    faiss.write_index(index, f"FAISS/{index_path}")

    with open(f"FAISS/{corpus_path}", "wb") as f:
        pickle.dump(original_texts, f)

    print("FAISS index and corpus updated successfully.")
