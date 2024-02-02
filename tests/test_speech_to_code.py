import pytest

from speech_to_code import speech_to_text


@pytest.mark.parametrize(
    "speech_file_path, expected_output_text",
    [
        ("tests/assets/fibonacci.m4a", "Please write me bla bla")
    ]
)
def test_speech_to_text(speech_file_path: str, expected_text: str) -> None:
    """Test that transcription functionality works correctly.

    Args:
        speech_file_path (str): File path to audio file containing speech.
        expected_text (str): Expected text transcription of provided speech file.
    """

    transcribed_text = speech_to_text(speech_file_path)
    assert transcribed_text == expected_text, f"Transcription didn't match speech in path {speech_file_path!r}"
