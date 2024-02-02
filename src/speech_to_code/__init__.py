"""Speech to code."""

from speech_to_code.pipelines import SpeechToCode, SpeechToText, TextToCode

from typing import Callable

def speech_to_code_pipeline(
    language_model_id: str = "microsoft/phi-2",
    stt_model_id: str = "distil-whisper/distil-small.en"
) -> Callable[[str], str | None]:
    speech_to_code = SpeechToCode(
        speech_to_text=SpeechToText(model_id=stt_model_id),
        text_to_code=TextToCode(model_id=language_model_id)
    )
    return speech_to_code.speech_to_code


__all__: list[str] = [
    "speech_to_code_pipeline",
]
