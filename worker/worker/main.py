"""Worker entrypoint."""

from azure.storage.blob.aio import BlobServiceClient
from azure.identity import DefaultAzureCredential
from azure.storage.queue import QueueServiceClient


credential = DefaultAzureCredential(managed_identity_client_id="f1fa9ae3-9815-465f-8a41-26a731203e31")

storage_blob_account_url = "https://speech46c96a79acf72d79.blob.core.windows.net"
storage_queue_account_url = "https://speech46c96a79acf72d79.queue.core.windows.net"

blob_service_client = BlobServiceClient(account_url=storage_blob_account_url, credential=credential)
queue_service_client = QueueServiceClient(account_url=storage_queue_account_url, credential=credential)

def process_queue(queue_name: str = "speechprocessing"):
    queue_client = queue_service_client.get_queue_client(queue_name)

    print("Listening to queue.")

    while True:
        messages = queue_client.receive_messages(max_messages=5)
        for message in messages.by_page():
            file_url = message.content
            print(f"Received message: {file_url!r}")
            queue_client.delete_message(message)

def start() -> None:
    print("Starting queue processing.")
    process_queue()
