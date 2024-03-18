"""Worker entrypoint."""


from azure.identity import DefaultAzureCredential
from azure.storage.blob.aio import BlobServiceClient
from azure.storage.queue import QueueServiceClient
from azure.data.tables import TableServiceClient
from azure.keyvault.secrets import SecretClient

import asyncio

import time
import json
import tempfile

from task.status import update_task
from task.models import TaskDescription

from speech_to_code import SpeechToCode

# TODO(in the future): Don't hardcode these magic strings.
credential = DefaultAzureCredential(managed_identity_client_id="f1fa9ae3-9815-465f-8a41-26a731203e31")
secret_client = SecretClient(vault_url="https://secrets7c08f48a1a533b26.vault.azure.net", credential=credential)
connection_string = secret_client.get_secret("storage-connection-string").value

# Persisted services used by worker:
speech_to_code = SpeechToCode.default()
blob_service_client = BlobServiceClient.from_connection_string(
    conn_str=connection_string
)
queue_service_client = QueueServiceClient.from_connection_string(
    conn_str=connection_string
)
table_service_client = TableServiceClient.from_connection_string(
    conn_str=connection_string
)


async def process_message(worker_message: TaskDescription) -> None:
    update_task(task_id=worker_message.task_id, status="processing")

    blob_client = blob_service_client.get_blob_client(
        container="content", blob=worker_message.blob_name
    )

    with tempfile.NamedTemporaryFile(suffix=".wav") as audio_file:
        blob_data = await blob_client.download_blob()
        await blob_data.readinto(audio_file)

        result = speech_to_code.convert(file_path=audio_file.name)
        update_task(task_id=worker_message.task_id, status="done", result=result)

    # Clean up processed file.
    await blob_client.delete_blob()


async def process_queue(queue_name: str = "speechprocessing"):
    queue_client = queue_service_client.get_queue_client(queue_name)

    print("Listening to queue.")

    while True:
        messages = queue_client.receive_messages(max_messages=1)
        for message in messages:
            worker_message: TaskDescription = TaskDescription(**json.loads(message.content))
            try:
                await process_message(worker_message)
                print("Finished task.")
            except Exception as e:
                print("Critical exception occured:", e)
                update_task(task_id=worker_message.task_id, status="queueing")

            # Clean up after job is done.
            queue_client.delete_message(message)

        time.sleep(1)


def start() -> None:
    print("Starting queue processing.")
    asyncio.run(process_queue())
