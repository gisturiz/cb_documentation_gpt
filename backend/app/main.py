import os
import openai
import pinecone
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

# openai key
openai.api_key = os.getenv("OPENAI_API_KEY") or "OPENAI_API_KEY"

# initialize connection to pinecone (get API key at app.pinecone.io)
api_key = os.getenv("PINECONE_API_KEY") or "PINECONE_API_KEY"
# find your environment next to the api key in pinecone console
env = os.getenv("PINECONE_ENVIRONMENT") or "PINECONE_ENVIRONMENT"
pinecone.init(api_key=api_key, enviroment=env)

# openai function without context
def complete(prompt):
    res = openai.Completion.create(
        engine='text-davinci-003',
        prompt=prompt,
        temperature=0,
        max_tokens=400,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        stop=None
    )
    return res['choices'][0]['text'].strip()


# connect to index
index_name = os.getenv("PINECONE_INDEX") or "PINECONE_INDEX"
index = pinecone.Index(index_name)

# choose embed model
embed_model = "text-embedding-ada-002"

limit = 3750
# get context from pinecone db


def retrieve(query):
    res = openai.Embedding.create(
        input=[query],
        engine=embed_model
    )

    # retrieve from Pinecone
    xq = res['data'][0]['embedding']

    # get relevant contexts
    res = index.query(xq, top_k=3, include_metadata=True)
    print(res)
    URL = res['matches'][0]['metadata']['url']
    contexts = [
        x['metadata']['text'] for x in res['matches']
    ]

    # build our prompt with the retrieved contexts included
    prompt_start = (
        "Answer the question based on the context below.\n\n" +
        "Context: you are a developer relations documentation bot. Answer the questions in a way which would be the most helpful for developers trying to get information from documentation, including API references, code samples when appropriate."
    )
    prompt_end = (
        f"\n\nQuestion: {query}\nAnswer:"
    )
    # append contexts until hitting limit
    for i in range(1, len(contexts)):
        if len("\n\n---\n\n".join(contexts[:i])) >= limit:
            prompt = (
                prompt_start +
                "\n\n---\n\n".join(contexts[:i-1]) +
                prompt_end
            )
            break
        elif i == len(contexts)-1:
            prompt = (
                prompt_start +
                "\n\n---\n\n".join(contexts) +
                prompt_end
            )
    return [prompt, URL]
class TextIn(BaseModel):
    text: str

class PredictionOut(BaseModel):
    question: str
    answer: str
    url: str

# initialize app
app = FastAPI()

# enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"health_check": "OK", "model_version": "0.0.1"}

@app.post("/predict", response_model=PredictionOut)
def predict(payload: TextIn):
    query_with_contexts = retrieve(payload.text)
    res = complete(query_with_contexts[0])
    url = query_with_contexts[1]
    return {"question": payload.text, "answer": res, "url": url}