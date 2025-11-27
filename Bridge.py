from fastapi import FastAPI, Request, HTTPException
from dotenv import load_dotenv
import os, requests

load_dotenv()

PAPERLESS_URL = os.getenv("PAPERLESS_URL")
PAPERLESS_TOKEN = os.getenv("PAPERLESS_TOKEN")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")
HEADERS ={"Authorization" : f"Token {PAPERLESS_TOKEN}", "Accept" : "application/json"}  

app = FastAPI(title="Bridge", version="0.0.1")

#get Documents von paperless-ngx
@app.post("/ingest")

async def ingest(request: Request):

    if WEBHOOK_SECRET:
        got = request.headers.get("x-webhook-token")
        if got != WEBHOOK_SECRET:
            raise HTTPException(status_code=401, detail="Invalid webhook token")
        

    data = await request.json()
    print("Webhook received raw body:", await request.body())
    print("Parsed JSON:", data)

    doc_id = data.get("document_id") or data.get("id")
    if not doc_id:
        raise HTTPException(status_code=400, detail="Missing document_id")
    
    url = f"{PAPERLESS_URL}/api/documents/{doc_id}/"
    response = requests.get(url, headers = HEADERS)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=f"Paperless error:{response.text}")
    
    document = response.json()


    print("[Ingest OK]",{"id": doc_id, "title" : document.get("title")} )
    return{"status": "ok", "paperless_id" : doc_id, "title" : document.get("title")} 

#server check
@app.get("/health")
def health():
    return{"ok":True}

#nur beim ausführen der datei
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("bridge:app", host="0.0.0.0", port = 8080, reload = False)
