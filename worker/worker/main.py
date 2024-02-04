"""Worker entrypoint."""

from azure.storage.blob.aio import BlobServiceClient
from azure.identity import DefaultAzureCredential
from azure.storage.queue import QueueServiceClient

import time

connection_string = "DefaultEndpointsProtocol=https;EndpointSuffix=core.windows.net;AccountName=speech46c96a79acf72d79;AccountKey=V2ti/mmKeneqq3WHGrDcFJ6kUEEK3lHVao8afNOsKXpmi07Gg5GGPdul94bh+EHsBWI7inPHcumG+ASt1c8BiQ==;BlobEndpoint=https://speech46c96a79acf72d79.blob.core.windows.net/;FileEndpoint=https://speech46c96a79acf72d79.file.core.windows.net/;QueueEndpoint=https://speech46c96a79acf72d79.queue.core.windows.net/;TableEndpoint=https://speech46c96a79acf72d79.table.core.windows.net/"

credential = DefaultAzureCredential(managed_identity_client_id="f1fa9ae3-9815-465f-8a41-26a731203e31")

storage_blob_account_url = "https://speech46c96a79acf72d79.blob.core.windows.net"
storage_queue_account_url = "https://speech46c96a79acf72d79.queue.core.windows.net"

blob_service_client = BlobServiceClient(account_url=storage_blob_account_url, credential=credential)
queue_service_client = QueueServiceClient.from_connection_string(conn_str=connection_string)

def process_queue(queue_name: str = "speechprocessing"):
    queue_client = queue_service_client.get_queue_client(queue_name)

    print("Listening to queue.")

    while True:
        messages = queue_client.receive_messages(max_messages=1)
        for message in messages:
            file_url = message.content
            print(f"Received message: {file_url!r}")
            queue_client.delete_message(message)

        time.sleep(1)

def start() -> None:
    print("Starting queue processing.")
    process_queue()
