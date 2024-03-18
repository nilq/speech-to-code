# Speech to Code API 🤗

FastAPI implementation of the web Speech to Code API.

## Get started

### Prerequisites

This package uses Poetry for dependency management.

### Running the API

1. Install the `api` using `poetry install`.
2. Run the API locally using `poetry run start`. (this calls `api.main:start`)

You will then be able to access the API on `http://0.0.0.0:8000/`.

> Note: You can control the port using the `PORT` environment variable. :)

## Routes

### `POST /task`

This is the entrypoint of the Speech to Code API. It accepts audio file upload via the request body form-data. To use it, hit it with a post request with a WAV-file submitted under the `audio` key.

This will create a new task, which is immediately queued.

#### Example request

Using `curl`, a request can be submitted with:

```
curl -X POST -F "audio=@example.wav" http://0.0.0.0:8000/task
```

This will return a HTTP 200, with contents similar to:

```json
{
    "task_id": "c92ecf6e14814c2a9289a3e276797e4c"
}
```

### `GET /task/<id>`

Once a task is queued, it may take some time for it to start processing, and subsequently to finish. This endpoint gets the current status of the task, and will provide the task result once it's done.

Simply send a GET request to the endpoint corresponding to the `task_id` received from `POST /task` to observe the status.

#### Example request

You can use this endpoint by `curl`'ing the route. Like this:

```
curl http://0.0.0.0:8000/task/c92ecf6e14814c2a9289a3e276797e4c
```

This will respond with a HTTP 200, containing the following (in chronological order):

1. In the queued state.

```json
{
    "status": "queueing",
    "result": null
}
```

2. When a processing worker has picked up the task.

```json
{
    "status": "processing",
    "result": null
}
```

3. When the task is done processing. 🎉

```json
{
    "status": "done",
    "result": "<code from speech>"
}
```

## Docker

Building the Docker image must be done from the root (`..` from here) context to include the `common` package. You can build the API image from the root directory containing `api/`, like this:

```
docker build -t speech-to-codeapi -f api/docker/Dockerfile .
```

> Note: This will require mounting relevant Azure credentials, or passing environment credentials to the container.
