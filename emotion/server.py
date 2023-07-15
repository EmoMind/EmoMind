from flask import Flask, request
import torch
import torchaudio
from transformers import Wav2Vec2FeatureExtractor, WavLMForSequenceClassification
import json


def emotion_inference(waveform, sample_rate):
    transform = torchaudio.transforms.Resample(sample_rate, 16000)
    data = transform(waveform)
    inputs = feature_extractor(
        data,
        sampling_rate=feature_extractor.sampling_rate,
        return_tensors="pt",
        padding=True,
        max_length=16000 * 10,
        truncation=True
    )
    logits = model(inputs['input_values'][0]).logits
    predictions = torch.argmax(logits, dim=-1)
    predicted_emotion = label2emotion[model2data[predictions.cpu().numpy()[0]]]

    return predicted_emotion


device = 'cpu'
model_name = 'xbgoose/wavlm-base-speech-emotion-recognition-russian-dusha-finetuned'
feature_extractor_name = 'microsoft/wavlm-base'

feature_extractor = Wav2Vec2FeatureExtractor.from_pretrained(feature_extractor_name)
model = WavLMForSequenceClassification.from_pretrained(model_name)

torch.set_num_threads(1)

label2emotion = {
    0: "нейтральное",
    1: "позитивное",
    2: "грустное",
    3: "злое",
    4: "другое"
}
model2data = {
    0: 0,
    1: 3,
    2: 1,
    3: 2,
    4: 4
}

app = Flask(__name__)


@app.route("/hello")
def hello():
    return "<p>Hello</p>"


@app.route("/get_emotion", methods=['POST'])
def get_emotion():
    content = request.json
    wav = torch.tensor(content["audio"])
    sr = int(content["sample_rate"])
    emotion = emotion_inference(wav, sr)
    dict_ = {
        'emotion': emotion
    }
    return json.dumps(dict_)
