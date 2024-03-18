# Common task

This directory is meant to contain common packages, shared between the API and worker - e.g. the shared messaging models and status interface.

## `task`

This package contains shared task management functionality used by the workers and API backend.

### `models`

A module containing Pydantic models for messaging between API and workers.

### `status`

A module containing helper functions to update task statuses in Azure Table Storage.
