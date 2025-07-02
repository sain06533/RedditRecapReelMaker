from TTS.api import TTS

# Load pre-trained TTS model
tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC", progress_bar=True).to("cuda")  # Use GPU

# Generate speech
tts.tts_to_file(
    text="Reddit recap begins now. Here's what people said. This is a fucking audio test!!",
    file_path="test_output.wav"
)
