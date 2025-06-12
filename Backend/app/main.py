from fastapi import FastAPI, File, UploadFile, Form, Request
from fastapi.middleware.cors import CORSMiddleware
import os
import json

from .extract_text import extract_text
from .clean_text import clean_text
from .create_chunks import split_text
from .add_metadata import add_metadata
from .embedd_chunks import embedd_chunks
from .faiss_store import faiss_store
from .fetch_data import fetch_data
from .llm_call import get_chat_completion
from .get_prompt import get_prompt

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/upload/")
async def upload_file(source: str = Form(...), file: UploadFile = File(...)):

    # Creating a temporary folder to hold the document
    os.makedirs("uploaded_docs",exist_ok=True)
    file_location = f"uploaded_docs/{file.filename}"
    with open(file_location,"wb") as f:
        f.write(await file.read())
        
    # Extracting the text
    text = extract_text(file_location)
    print("Extraction completed")
    
    # Cleaning the extracted text
    cleaned_text = clean_text(text)
    print("Cleaning completed")
    
    # Creating chunks
    chunks = split_text(cleaned_text)
    print("Splitting completed")
    
    # Add metadata 
    chunks_with_metadata = add_metadata(chunks,source)
    print("Metadata addition completed")
    
    # Convert the chunks into vectors (Embedding)
    embedded_chunks = embedd_chunks(chunks_with_metadata)
    # for i,chunk in enumerate(embedded_chunks):
    #     print(f"Chunk {i+1}: ",chunk[:5])
    print("Embedding completed")
    
    # Store the embedding in FAISS
    faiss_store(embedded_chunks,chunks_with_metadata,source)
      
    # Removing the temporary folder
    os.remove(f"uploaded_docs/{file.filename}")
    os.rmdir("uploaded_docs")
    
    return chunks_with_metadata 


@app.post("/recievePrompt/")
async def recieve_prompt(request: Request):
    
    body = await request.body()
    data = json.loads(body.decode("utf-8"))

    prompt_str = data.get("inputValue")
    model_str = data.get("model")
    project = data.get("project")
    
    response = fetch_data(prompt_str,project)

    context_section = "\n".join([f"Context {i+1}: {chunk}" for i, chunk in enumerate(response)])
    
    final_prompt = get_prompt(prompt_str, context_section)

    answer = get_chat_completion(final_prompt, model_str)
    
    return answer