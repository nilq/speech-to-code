import uvicorn
import os

from fastapi import FastAPI, UploadFile, File
from azure.storage.blob.aio import BlobServiceClient
from azure.identity import DefaultAzureCredential
from azure.storage.queue import QueueServiceClient

import uuid


credential = DefaultAzureCredential(managed_identity_client_id="f1fa9ae3-9815-465f-8a41-26a731203e31")
storage_account_url = "https://speech46c96a79acf72d79.blob.core.windows.net"
blob_service_client = BlobServiceClient(account_url=storage_account_url, credential=credential)
queue_service_client = QueueServiceClient(storage_account_url=storage_account_url, credential=credential)

queue_name = "speechprocessing"

app = FastAPI()

def random_audio_file_name() -> str:
    return uuid.uuid4().hex


@app.post("/speech")
async def speak(audio: UploadFile = File(...)):
    # TODO: Error when not WAV. That's the only thing we want.

    # Propagate speech to blob storage.
    blob_client = blob_service_client.get_blob_client(container="speech", blob=random_audio_file_name)
    await blob_client.upload_blob(audio.file.read())

    # Send work message to queue.
    queue_client = queue_service_client.get_queue_client(queue_name)
    await queue_client.send_message(blob_client.url)


@app.get("/health")
def health() -> None:
    ...


def start():
    port: int = int(os.getenv("PORT", 8000))
    uvicorn.run("api.main:app", host="0.0.0.0", port=port)
