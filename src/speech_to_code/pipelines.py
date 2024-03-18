"""Speech to code pipeline components."""

import torch

from string import Template
from speech_to_code.utils import (
    load_and_resample_audio,
    WHISPER_SAMPLE_RATE,
    first_code_block_from_text,
)
from transformers import (
    WhisperProcessor,
    WhisperForConditionalGeneration,
    AutoModelForCausalLM,
    AutoTokenizer,
    AutoConfig,
)

from typing import Self


# TODO(in the future): make use of HuggingFace transcription pipeline for more flexibility.
class SpeechToText:
    """Speech-to-text using pre-trained HuggingFace model."""
    def __init__(self, model_id: str = "distil-whisper/distil-small.en") -> None:
        """Initialise speech-to-text converter.
        Args:
            model_id (str, optional): Model ID of Whisper-like model.
                Defaults to "distil-whisper/distil-small.en".
        """
        model_config = AutoConfig.from_pretrained(model_id)
        if model_config.model_type != "whisper":
            raise ValueError(
                f"SpeechToText assumes a Whisper architecture, and isn't compatible with {model_id!r}"
            )

        self.model = WhisperForConditionalGeneration.from_pretrained(
            model_id,
            torch_dtype=torch.float32,
            low_cpu_mem_usage=True,
            use_safetensors=True,
        )
        self.processor = WhisperProcessor.from_pretrained(model_id)

    def convert(self, file_path: str) -> str:
        """Convert speech stored at provided WAV-file path to text.

        Args:
            file_path (str): Path to audio WAV-file containing speech.

        Returns:
            str: Text from provided speech file.
        """
        # This will always automatically resample to 16kHz (expected by Whisper).
        waveform_audio_data = load_and_resample_audio(
            file_path=file_path, sampling_rate=WHISPER_SAMPLE_RATE
        )
        input_features = self.processor(
            waveform_audio_data.squeeze(),
            sampling_rate=WHISPER_SAMPLE_RATE,
            return_tensors="pt",
        ).input_features
        predicted_ids = self.model.generate(input_features)
        return self.processor.batch_decode(predicted_ids, skip_special_tokens=True)[0]


class TextToCode:
    """Text-to-code using pre-trained HuggingFace model."""

    # Simple prompt template to frame transcription input.
    PROMPT = Template(
        "Instruct: Write the code according to the following speech-to-text transcription: $code_description\n"
        "Output:"
    )

    def __init__(
        self,
        model_id: str = "microsoft/phi-2",
    ) -> None:
        """Initialise text-to-code model.

        Args:
            model_id (str, optional): Model ID of autoregressive code/language model.
                Defaults to "microsoft/phi-2".
        """
        # TODO(in the future): Don't necessarily trust remote code.
        self.model = AutoModelForCausalLM.from_pretrained(
            model_id, trust_remote_code=True, low_cpu_mem_usage=True
        )
        self.tokenizer = AutoTokenizer.from_pretrained(
            model_id, trust_remote_code=True
        )

    def convert(self, text: str, max_length: int = 512) -> str:
        """Convert text to code using prompted language model.

        Note:
            Depending on the input `text`, this function is
            not at all guaranteed to output code. We try our best.

        Args:
            text (str): Text prompt contents (will be inserted into `TextToCode.PROMPT`).
            max_length (int, optional): Max token length to generate.
                Defaults to 512.

        Returns:
            str: Code/output of model.
        """
        final_prompt = TextToCode.PROMPT.substitute(code_description=text)

        inputs = self.tokenizer(
            final_prompt, return_tensors="pt", return_attention_mask=False
        )
        outputs = self.model.generate(**inputs, max_length=max_length)
        text = self.tokenizer.batch_decode(outputs)[0]

        # Return either first fenced (```...```) code block.
        # Usually the default prompt will make the model simply output the code directly after "Output: ".
        return first_code_block_from_text(text) or text.split("Output:")[1].strip()


class SpeechToCode:
    """Speech-to-code using pre-trained HuggingFace model."""
    def __init__(self, speech_to_text: SpeechToText, text_to_code: TextToCode) -> None:
        """Initialise speech-to-code composed of speech-to-text and text-to-code modules.

        Args:
            speech_to_text (SpeechToText): Speech-to-text component.
            text_to_code (TextToCode): Text-to-code component.
        """
        self.speech_to_text = speech_to_text
        self.text_to_code = text_to_code

    @classmethod
    def from_model_names(
        cls,
        language_model_id: str = "microsoft/phi-2",
        speech_to_text_model_id: str = "distil-whisper/distil-small.en",
    ) -> Self:
        """Create speech-to-code using model names/IDs.

        Args:
            language_model_id (str, optional): Model ID of autoregressive code/language model.
                Defaults to "microsoft/phi-2".
            speech_to_text_model_id (str, optional): Model ID of Whisper-like model.
                Defaults to "distil-whisper/distil-small.en".

        Returns:
            Self: A `SpeechToCode` object, ready to use.
        """
        speech_to_code = cls(
            speech_to_text=SpeechToText(model_id=speech_to_text_model_id),
            text_to_code=TextToCode(model_id=language_model_id),
        )
        return speech_to_code

    @classmethod
    def default(cls) -> Self:
        """Get default SpeechToCode pipeline.

        Returns:
            Self: A `SpeechToCode` object, ready to use.
        """
        return cls.from_model_names()

    def convert(self, file_path: str, max_code_length: int = 512) -> str:
        """Convert speech at specified file path to code.

        Args:
            file_path (str): Path to audio WAV-file containing speech.
            max_code_length (int, optional): Max token length of generated code.
                Defaults to 512.

        Returns:
            str: Code from provided speech file.
        """
        text: str = self.speech_to_text.convert(file_path=file_path)
        return self.text_to_code.convert(text=text, max_length=max_code_length)
