from fastapi import FastAPI, File, UploadFile, Form, Request
from fastapi.middleware.cors import CORSMiddleware
import os
import json
from typing import List
from sentence_transformers import SentenceTransformer


from .extract_text import extract_text  
from .clean_text import clean_text
from .create_chunks import split_text
from .add_metadata import add_metadata
from .embedd_chunks import embedd_chunks
from .faiss_store import faiss_store
from .fetch_data import fetch_data
from .llm_call import get_chat_completion   
from .llm_call import get_chat_completion_without_context
from .get_prompt import get_prompt
from .validate_url import validate_url  
app = FastAPI()

# model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
model = SentenceTransformer('all-mpnet-base-v2')

MAPPING_FILE = "source_url_map.json"
try:
    with open(MAPPING_FILE) as f:   
        data = json.load(f)
        origins = [url.rstrip("/") for url in data.values()]
except Exception:
    origins = []

if not origins:
    origins = ["*"]
    
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def load_mappings():
    if os.path.exists(MAPPING_FILE):
        with open(MAPPING_FILE, "r") as f:
            return json.load(f)
    return {}

def save_mappings(mappings):
    with open(MAPPING_FILE, "w") as f:
        json.dump(mappings, f, indent=4)

@app.post("/upload/")
async def upload_file(url:str = Form(...),source: str = Form(...), files: List[UploadFile] = File(...)):
    
    mappings = load_mappings()
    flag = False
    for s in mappings.keys():
        if source in s:
            flag = True
            break
    if not flag:
        mappings[source] = url
        save_mappings(mappings)
    
    for file in files:
        os.makedirs("uploaded_docs",exist_ok=True)
        file_location = f"uploaded_docs/{file.filename}"
        with open(file_location,"wb") as f:
            f.write(await file.read())
            
        text = extract_text(file_location)
        
        cleaned_text = clean_text(text.lower())
    
        chunks = split_text(cleaned_text)
        
        chunks_with_metadata = add_metadata(chunks,source)
        
        embedded_chunks = embedd_chunks(chunks_with_metadata,model)
        
        faiss_store(embedded_chunks,chunks_with_metadata,source)
        
        os.remove(f"uploaded_docs/{file.filename}")
        os.rmdir("uploaded_docs")
        print(f"{file.filename} Uploaded.")
        
    return "Success"


@app.post("/recievePrompt/")
async def recieve_prompt(request: Request):
    body = await request.body()
    data = json.loads(body.decode("utf-8"))

    prompt_str = data.get("inputValue")
    model_str = data.get("model")
    project = data.get("project")
    
    if project == "AI Assistant":
        return get_chat_completion_without_context(prompt_str, model_str)
    
    response = fetch_data(prompt_str,project,model)
    
    context_section = "\n".join([f"Context {i+1}: {chunk}" for i, chunk in enumerate(response)])
    
    final_prompt = get_prompt(prompt_str, context_section)

    answer = get_chat_completion(final_prompt, model_str)
    return answer

@app.get("/fetchProjects/")
async def fetchProjects(request: Request):
    url = request.query_params.get("url") 
    if not url:
        return {"error": "Missing 'url' query parameter"}

    return validate_url(str(url))

@app.get("/fetchAllProjects/")
async def fetchAllProjects(request: Request):
    return os.listdir("FAISS")



