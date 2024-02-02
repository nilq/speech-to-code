"""Speech to code"""

import torch

from string import Template
from speech_to_code.utils import load_and_resample_audio, WHISPER_SAMPLE_RATE, first_code_block_from_text
from transformers import WhisperProcessor, WhisperForConditionalGeneration, AutoModelForCausalLM, AutoTokenizer, AutoConfig


class SpeechToText:
    def __init__(self, model_id: str = "distil-whisper/distil-small.en") -> None:
        model_config = AutoConfig.from_pretrained(model_id)
        if model_config.model_type != "whisper":
            raise ValueError(f"SpeechToText assumes a Whisper architecture, and isn't compatible with {model_id!r}")

        self.model = WhisperForConditionalGeneration.from_pretrained(
            model_id,
            torch_dtype=torch.float32,
            low_cpu_mem_usage=True,
            use_safetensors=True
        )
        self.processor = WhisperProcessor.from_pretrained(model_id)

    def speech_to_text(self, file_path: str) -> str:
        waveform_audio_data = load_and_resample_audio(file_path=file_path, sampling_rate=WHISPER_SAMPLE_RATE)
        input_features = self.processor(
            waveform_audio_data.squeeze(),
            sampling_rate=WHISPER_SAMPLE_RATE,
            return_tensors="pt"
        ).input_features
        predicted_ids = self.model.generate(input_features)
        return self.processor.batch_decode(predicted_ids, skip_special_tokens=True)[0]


class TextToCode:
    PROMPT = Template(
        "Instruct: Write the code according to the following speech-to-text transcription: $code_description\n"
        "Output:"
    )

    def __init__(
        self,
        model_id: str = "microsoft/phi-2",
    ) -> None:
        self.model = AutoModelForCausalLM.from_pretrained(
            model_id,
            trust_remote_code=True,
            low_cpu_mem_usage=True
        )
        self.tokenizer = AutoTokenizer.from_pretrained("microsoft/phi-2", trust_remote_code=True)

    def text_to_code(self, text: str, max_length: int = 512) -> str | None:
        final_prompt = TextToCode.PROMPT.substitute(code_description=text)

        inputs = self.tokenizer(final_prompt, return_tensors="pt", return_attention_mask=False)
        outputs = self.model.generate(**inputs, max_length=max_length)
        text = self.tokenizer.batch_decode(outputs)[0]

        return first_code_block_from_text(text) or text


class SpeechToCode:
    def __init__(
        self,
        speech_to_text: SpeechToText,
        text_to_code: TextToCode
    ) -> None:
        self.speech_to_text = speech_to_text.speech_to_text
        self.text_to_code = text_to_code.text_to_code

    def speech_to_code(self, file_path: str) -> str | None:
        text: str = self.speech_to_text(file_path=file_path)
        return self.text_to_code(text=text)
