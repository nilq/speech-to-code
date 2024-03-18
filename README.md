# Speech to Code

Let’s use freely available HuggingFace models to make programming more accessible.

## Get started

### Environment

This project is set up to use Conda for managing the Python dependency, and uses Poetry for managing Python package dependencies.

**Set up the environment using Conda.**

```
$ conda env create -f conda.yaml
$ conda activate speech-to-code
```

This will give you a fresh Python 3.11 environment.

**Install Poetry.**

If you have not done this, I reccomend looking at the [official guide](https://python-poetry.org/docs/#installing-with-pipx).

### Install `speech_to_code`

This can be done by using e.g. Poetry for installing the package at the root, using `poetry install`.

### Usage

The most basic usage looks like the following.

```
from speech_to_code import SpeechToCode

converter = SpeechToCode.default()
converter.convert(file_path="path/to/audio.wav")
```

This will create a speech-to-code pipeline composed of Distil-Whisper (`distil-small.en`) and Phi-2.


## API

For details on how to run the API, please refer to the [`api/README.md`](api/README.md).
