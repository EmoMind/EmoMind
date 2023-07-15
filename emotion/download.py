from transformers import Wav2Vec2FeatureExtractor, WavLMForSequenceClassification

model_name = 'xbgoose/wavlm-base-speech-emotion-recognition-russian-dusha-finetuned'
feature_extractor_name = 'microsoft/wavlm-base'

feature_extractor = Wav2Vec2FeatureExtractor.from_pretrained(feature_extractor_name)
model = WavLMForSequenceClassification.from_pretrained(model_name)