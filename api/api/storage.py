"""Storage utilities."""

from azure.storage.blob.aio import BlobServiceClient
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()
blob_service_client = BlobServiceClient(credential=credential)

async def upload_file_to_azure() -> None:
    ...
