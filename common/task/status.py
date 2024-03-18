"""Task status updates."""

from task.models import StatusEntity, Status, StatusResult
from azure.data.tables import TableServiceClient, UpdateMode

connection_string = "DefaultEndpointsProtocol=https;EndpointSuffix=core.windows.net;AccountName=speech46c96a79acf72d79;AccountKey=V2ti/mmKeneqq3WHGrDcFJ6kUEEK3lHVao8afNOsKXpmi07Gg5GGPdul94bh+EHsBWI7inPHcumG+ASt1c8BiQ==;BlobEndpoint=https://speech46c96a79acf72d79.blob.core.windows.net/;FileEndpoint=https://speech46c96a79acf72d79.file.core.windows.net/;QueueEndpoint=https://speech46c96a79acf72d79.queue.core.windows.net/;TableEndpoint=https://speech46c96a79acf72d79.table.core.windows.net/"
table_service_client = TableServiceClient.from_connection_string(
    conn_str=connection_string
)
table_client = table_service_client.get_table_client(table_name="statustable")


def queue_task(task_id: str) -> None:
    """Queue new task by ID.

    This function creates a new entity in Azure Table Storage.

    Args:
        task_id (str): ID of task to queue.
    """
    entity = table_client.create_entity(
        StatusEntity(RowKey=task_id, status="queueing").dict()
    )
    print("Queued task in table", entity)


def update_task(task_id: str, status: Status, result: str | None = None) -> None:
    """Update existing task status entity.

    This will merge status and optional result into the task status entity.

    Args:
        task_id (str): ID of task to update status of.
        status (Status): New status.
        result (str | None, optional): Task result, if applicable to status.
            Defaults to None.
    """
    status_entity = StatusEntity(
        **table_client.get_entity(partition_key="status", row_key=task_id)
    )
    status_entity.status = status

    if result is not None:
        status_entity.result = result

    table_client.update_entity(mode=UpdateMode.MERGE, entity=status_entity)


def status_of_task(task_id: str) -> StatusResult:
    """Get status of task by ID.

    Args:
        task_id (str): ID of task to get status of.

    Returns:
        StatusResult: Current status of relevant task.
    """
    status_entity = StatusEntity(
        **table_client.get_entity(partition_key="status", row_key=task_id)
    )
    return StatusResult(status=status_entity.status, result=status_entity.result)
