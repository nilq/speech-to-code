import uvicorn
import os

from fastapi import FastAPI, UploadFile, File
from azure.storage.blob.aio import BlobServiceClient
from azure.identity import DefaultAzureCredential

import asyncio

credential = DefaultAzureCredential()
storage_account_url = "https://speech46c96a79acf72d79.blob.core.windows.net"
blob_service_client = BlobServiceClient(account_url=storage_account_url, credential=credential)

blob_client = blob_service_client.get_blob_client(container="content", blob="test")
with open(__file__, "rb") as data:
    asyncio.run(blob_client.upload_blob(data))


app = FastAPI()


@app.post("/speech")
async def speak(audio: UploadFile = File(...)):
    return { "filename": audio.filename }


@app.get("/health")
def health() -> None:
    ...


def start():
    port: int = int(os.getenv("PORT", 8000))
    uvicorn.run("api.main:app", host="0.0.0.0", port=port)
