# Speech to Code

This module contains the speech-to-code functionality.

## Get started

### Install `speech_to_code`

This can be done by installing the package at the root of the directory containing the `src` directory (i.e. `../../` from here).

### Usage

The most basic usage looks like the following.

```
from speech_to_code import SpeechToCode

converter = SpeechToCode.default()
converter.convert(file_path="path/to/audio.wav")
```

This will create a speech-to-code pipeline composed of Distil-Whisper (`distil-small.en`) and Phi-2.

## Components

### `pipelines`

This module contains `SpeechToText`, `TextToCode`, and the end-to-end `SpeechToCode` pipelines.

### `utils`

This module contains utilities for resampling audio, and for extracting code fence contents from a string.
