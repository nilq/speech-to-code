import torch
import torchaudio
import re

WHISPER_SAMPLE_RATE = 16_000

def load_and_resample_audio(file_path: str, sampling_rate=WHISPER_SAMPLE_RATE) -> torch.Tensor:
    waveform, sample_rate = torchaudio.load(file_path)
    return torchaudio.functional.resample(waveform, orig_freq=sample_rate, new_freq=WHISPER_SAMPLE_RATE)

def code_blocks_from_text(text: str) -> list[str]:
    pattern = r"```(\w+\n)?(.*?)```"
    matches = re.findall(pattern, text, re.DOTALL)

    return [match[1].strip() for match in matches]

def first_code_block_from_text(text: str) -> str | None:
    return (code_blocks_from_text(text=text) or [None])[0]
