import uvicorn
import os

from fastapi import FastAPI, UploadFile, File, HTTPException
from azure.storage.blob.aio import BlobServiceClient
from azure.identity import DefaultAzureCredential
from azure.storage.queue import QueueServiceClient

import uuid


credential = DefaultAzureCredential(managed_identity_client_id="f1fa9ae3-9815-465f-8a41-26a731203e31")

storage_blob_account_url = "https://speech46c96a79acf72d79.blob.core.windows.net"
storage_queue_account_url = "https://speech46c96a79acf72d79.blob.core.windows.net"

blob_service_client = BlobServiceClient(account_url=storage_blob_account_url, credential=credential)

connection_string = "DefaultEndpointsProtocol=https;EndpointSuffix=core.windows.net;AccountName=speech46c96a79acf72d79;AccountKey=V2ti/mmKeneqq3WHGrDcFJ6kUEEK3lHVao8afNOsKXpmi07Gg5GGPdul94bh+EHsBWI7inPHcumG+ASt1c8BiQ==;BlobEndpoint=https://speech46c96a79acf72d79.blob.core.windows.net/;FileEndpoint=https://speech46c96a79acf72d79.file.core.windows.net/;QueueEndpoint=https://speech46c96a79acf72d79.queue.core.windows.net/;TableEndpoint=https://speech46c96a79acf72d79.table.core.windows.net/"

queue_name = "speechprocessing"
queue_service_client = QueueServiceClient.from_connection_string(conn_str=connection_string)
queue_client = queue_service_client.get_queue_client(queue_name)


app = FastAPI()

def random_audio_file_name() -> str:
    return uuid.uuid4().hex


@app.post("/speech")
async def speak(audio: UploadFile = File(...)):
    if not audio.filename.endswith(".wav"):
        raise HTTPException(status_code=400, detail="Invalid file type. Only WAV files are accepted.")

    # Propagate speech to blob storage.
    blob_client = blob_service_client.get_blob_client(container="content", blob=f"{random_audio_file_name()}.wav")
    audio_file = await audio.read()
    await blob_client.upload_blob(audio_file, blob_type="BlockBlob")

    print("Uploaded blob.", blob_client.url)

    # Send work message to queue.
    queue_client.send_message(blob_client.url)


@app.get("/health")
def health() -> None:
    ...


def start():
    port: int = int(os.getenv("PORT", 8000))
    uvicorn.run("api.main:app", host="0.0.0.0", port=port)
