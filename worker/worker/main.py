"""Worker entrypoint."""

from azure.storage.blob.aio import BlobServiceClient
from azure.identity import DefaultAzureCredential
from azure.storage.queue import QueueServiceClient

import asyncio

credential = DefaultAzureCredential(managed_identity_client_id="f1fa9ae3-9815-465f-8a41-26a731203e31")
storage_account_url = "https://speech46c96a79acf72d79.blob.core.windows.net"
blob_service_client = BlobServiceClient(account_url=storage_account_url, credential=credential)
queue_service_client = QueueServiceClient(account_url=storage_account_url, credential=credential)

blob_client = blob_service_client.get_blob_client(container="content", blob="testfromworker")
with open(__file__, "rb") as data:
    asyncio.run(blob_client.upload_blob(data))


async def process_queue():
    queue_name = "speechprocessing"
    queue_client = queue_service_client.get_queue_client(queue_name)

    async with queue_client:
        while True:
            messages = await queue_client.receive_messages()
            for message in messages:
                file_url = message.content
                print(f"Received message: {file_url!r}")
                await queue_client.delete_message(message)
            await asyncio.sleep(1)


def start() -> None:
    asyncio.run(process_queue())
