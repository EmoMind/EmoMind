from flask import Flask, request
import torch
import torchaudio
from transformers import BertTokenizerFast, Wav2Vec2FeatureExtractor
import json
import torch.nn as nn

import __main__

device = 'cpu'

class Net(nn.Module):
    def __init__(self, text_model, audio_model):
        super(Net, self).__init__()
        self.text_model = text_model
        self.audio_model = audio_model

        self.classifier = nn.Sequential(
            nn.Dropout(p=0.1),
            nn.Linear(1280, 1280, bias=True),
            nn.LeakyReLU(),
            nn.Dropout(p=0.1),
            nn.Linear(1280, 256, bias=True),
            nn.LeakyReLU(),
            nn.Dropout(p=0.1),
            nn.Linear(256, 64, bias=True),
            nn.LeakyReLU(),
            nn.Dropout(p=0.1),
            nn.Linear(64, 5, bias=True)
        )

        self.emotion2label = {
            "neutral":0,
            "positive":1,
            "sad":2,
            "angry":3,
            "other":4
        }


    def tokenize_function(self, text):
        tokenized = tokenizer(text, max_length=512, padding='max_length', return_tensors='pt')
        return torch.cat([tokenized['input_ids'],
                          tokenized['token_type_ids'],
                          tokenized['attention_mask']], 0)

    def get_input(self, filepath):
        waveform, sample_rate = torchaudio.load(filepath, normalize=True)
        transform = torchaudio.transforms.Resample(sample_rate, 16000)
        waveform = transform(waveform)

        inputs = feature_extractor(
                waveform,
                sampling_rate=feature_extractor.sampling_rate,
                return_tensors="pt",
                padding=True,
                max_length=16000 * 10,
                truncation=True
        )
        return inputs['input_values'][0]

    def forward(self, text_data, inputs):
        b_input_ids, b_type_ids, b_input_mask,  = text_data[:, 0, :], text_data[:, 1, :], text_data[:, 2, :]
        logits_a = self.text_model(
                       b_input_ids.to(device).long(),
                       b_input_mask.to(device),
                       b_type_ids.to(device).long(),
                       output_hidden_states=True
                      )['hidden_states'][-1][:,:,-1]

        logits_b = self.audio_model(inputs.to(device))['hidden_states'][-1][:,-1,:]
        concatenated_vectors = torch.cat([logits_a.to(device), logits_b.to(device)], 1)

        output = self.classifier(concatenated_vectors)
        del concatenated_vectors, logits_a, logits_b, text_data, inputs
        return output

tokenizer = BertTokenizerFast.from_pretrained('Aniemore/rubert-tiny2-russian-emotion-detection')
feature_extractor = Wav2Vec2FeatureExtractor.from_pretrained("facebook/hubert-base-ls960")

num2emotion = {0: 'neutral', 1: 'angry', 2: 'positive', 3: 'sad', 4: 'other'}


setattr(__main__, "Net", Net)
model = torch.load('model.pth', map_location=torch.device("cpu"))


def emotion_inference(wav, sr, text):
    transform = torchaudio.transforms.Resample(sr, 16000)
    waveform = transform(torch.tensor(wav))

    inputs = feature_extractor(
        waveform,
        sampling_rate=feature_extractor.sampling_rate,
        return_tensors="pt",
        padding=True,
        max_length=16000 * 10,
        truncation=True
    )

    tokenized = tokenizer(text, max_length=512, padding='max_length', return_tensors='pt')
    tokenized = torch.cat([tokenized['input_ids'],
                           tokenized['token_type_ids'],
                           tokenized['attention_mask']], 0)

    logits = model(torch.unsqueeze(tokenized, 0), inputs['input_values'][0])
    predictions = torch.argmax(logits, dim=-1)
    predicted_emotion = num2emotion[int(predictions.cpu().detach())]
    return predicted_emotion

torch.set_num_threads(1)

app = Flask(__name__)

@app.route("/get_emotion", methods=["POST"])
def get_emotion():
    content = request.json
    wav = torch.tensor(content["audio"])
    sr = int(content["sample_rate"])
    text = content["text"]
    emotion = emotion_inference(wav, sr, text)
    dict_ = {
        'emotion': emotion
    }
    return json.dumps(dict_)


# with open('model.pth', 'rb') as file:
#     model = torch.load(file)