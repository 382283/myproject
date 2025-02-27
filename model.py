from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import pandas as pd

model = AutoModelForSequenceClassification.from_pretrained("jarvisx17/japanese-sentiment-analysis")
tokenizer = AutoTokenizer.from_pretrained("jarvisx17/japanese-sentiment-analysis")

def predict_sentiment(text):
    nlp = pipeline("sentiment-analysis", model=model, tokenizer=tokenizer)
    result = nlp(text)
    return result


