"""Speech to Code API entrypoint."""

import uvicorn
import os

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from azure.storage.blob.aio import BlobServiceClient
from azure.storage.queue import QueueServiceClient
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

import uuid
import json

from task.models import TaskDescription
from task.status import queue_task, status_of_task

# Credentials to reach KeyVault.
credential = DefaultAzureCredential(managed_identity_client_id="f1fa9ae3-9815-465f-8a41-26a731203e31")

# NOTE: When spinning up new infrastructure (from scratch), this needs to be changed.
secret_client = SecretClient(vault_url="https://secrets7c08f48a1a533b26.vault.azure.net", credential=credential)

# Get connection string from KeyVault secret.
connection_string = secret_client.get_secret("storage-connection-string").value

blob_service_client = BlobServiceClient.from_connection_string(
    conn_str=connection_string
)

# TODO(in the future): Don't hardcode this magic identifier.
queue_name = "speechprocessing"
queue_service_client = QueueServiceClient.from_connection_string(
    conn_str=connection_string
)
queue_client = queue_service_client.get_queue_client(queue_name)


app = FastAPI()


def random_task_id() -> str:
    """Get random task ID.

    Returns:
        str: UUID4 hex to serve as random task ID..
    """
    return uuid.uuid4().hex


@app.post("/task")
async def submit_task(audio: UploadFile = File(...)) -> JSONResponse:
    """Submit a new speech-to-code task.

    Note:
        Once a task is submitted, use the `get_task` endpoint to get the status
        and (eventually) resutl of the task.

    Args:
        audio (UploadFile): File upload via body form-data ("audio" key, must be WAV).

    Returns:
        JSONResponse: Response containing `{ "task_id": ... }` of submitted task.
    """
    if not audio.filename.endswith(".wav"):
        raise HTTPException(
            status_code=400, detail="Invalid file type. Only WAV files are accepted."
        )

    # Task information.
    task_id: str = random_task_id()
    blob_name: str = f"{task_id}.wav"

    # Propagate speech to blob storage.
    blob_client = blob_service_client.get_blob_client(
        container="content", blob=blob_name
    )
    audio_file = await audio.read()
    await blob_client.upload_blob(audio_file, blob_type="BlockBlob")

    print("Uploaded blob:", blob_client.url)

    # Initialise task in status table.
    queue_task(task_id=task_id)

    # Send work message to queue.
    queue_client.send_message(
        json.dumps(TaskDescription(task_id=task_id, blob_name=blob_name).dict())
    )

    # Here you go.
    return JSONResponse(content={"task_id": task_id})


@app.get("/task/{id}")
def get_task(id: str) -> JSONResponse:
    """Get task status and result.

    Note:
        This will always return the current status of the task.
        However, "result" will be `null` until the task is done
        as indicated by `{ "result": "done", ... }`.

    Args:
        id (str): ID of task to get status/result of.

    Returns:
        JSONResponse: Object containing "status" and "result".
    """
    return JSONResponse(content=jsonable_encoder(status_of_task(task_id=id)))


@app.get("/health")
def health() -> None:
    """Simplest possible health check."""
    ...


def start() -> None:
    """Start the API!"""
    port: int = int(os.getenv("PORT", 8000))
    uvicorn.run("api.main:app", host="0.0.0.0", port=port)
