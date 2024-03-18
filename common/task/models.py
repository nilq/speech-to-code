"""Task message models."""

from pydantic import BaseModel, Field

from typing import Literal

Status = Literal["queueing", "processing", "done"]
PartitionKey: str = "status"

class StatusEntity(BaseModel):
    """Status entity model of status records in Azure Table Storage."""
    # These are used for lookup in Azure Table Storage.
    PartitionKey: str = PartitionKey
    RowKey: str = Field(..., description="ID of the task.")

    # Actual task entity contents.
    status: Status = Field(default="queueing", description="Status of task.")
    result: str | None = Field(
        default=None, description="Task result, set once task is done."
    )


class TaskDescription(BaseModel):
    """Model of task description."""
    blob_name: str = Field(
        ..., description="Audio file blob name, for Azure Blob Storage retrieval."
    )
    task_id: str = Field(
        ..., description="Worker task ID, used for updating status of task."
    )


class StatusResult(BaseModel):
    """Result of a status request, representing current status of a task."""
    status: Status = Field(default="queueing", description="Status of task.")
    result: str | None = Field(
        default=None, description="Task result, set once task is done."
    )
