import torch
import torchaudio
import re

WHISPER_SAMPLE_RATE = 16_000


def load_and_resample_audio(
    file_path: str, sampling_rate=WHISPER_SAMPLE_RATE
) -> torch.Tensor:
    """Load and resample audio from path.

    Args:
        file_path (str): Path to audio file.
        sampling_rate (int, optional): Target sampling rate.
            Defaults to `WHISPER_SAMPLE_RATE` (16kHz).

    """
    waveform, sample_rate = torchaudio.load(file_path)
    return torchaudio.functional.resample(
        waveform, orig_freq=sample_rate, new_freq=WHISPER_SAMPLE_RATE
    )


def code_blocks_from_text(text: str) -> list[str]:
    """Extract fenced Markdown code blocks from text.

    Args:
        text (str): Text that might contain code.

    Returns:
        list[str]: List of extracted code blocks.
    """
    pattern = r"```(\w+\n)?(.*?)```"
    matches = re.findall(pattern, text, re.DOTALL)

    return [match[1].strip() for match in matches]


def first_code_block_from_text(text: str) -> str | None:
    """Get first fenced code block from text (if one exists).

    Args:
        text (str): Text that might contain code.

    Returns:
        str | None: Code string, or None if no fenced code was found.
    """
    return (code_blocks_from_text(text=text) or [None])[0]
