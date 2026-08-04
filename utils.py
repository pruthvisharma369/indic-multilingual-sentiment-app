import torch

from transformers import AutoTokenizer
from transformers import AutoModelForSequenceClassification

from config import MODEL_PATH
from config import MAX_LENGTH
from config import LABELS


print("Loading your trained IndicBERT model...")

tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)

model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)

model.eval()

print("Model Loaded Successfully!")

def predict_sentiment(text):

    # Tokenize the input text
    inputs = tokenizer(
        text,
        max_length=MAX_LENGTH,
        padding="max_length",
        truncation=True,
        return_tensors="pt"
    )

    # Disable gradient calculation
    with torch.no_grad():

        outputs = model(**inputs)

    # Convert logits into probabilities
    probabilities = torch.softmax(outputs.logits, dim=1)

    confidence, prediction = torch.max(probabilities, dim=1)

    sentiment = LABELS[prediction.item()]

    return sentiment, confidence.item()


#temporary code
if __name__ == "__main__":

    sentence = input("Enter sentence: ")

    sentiment, confidence = predict_sentiment(sentence)

    print()

    print("Prediction :", sentiment)

    print("Confidence :", round(confidence * 100, 2), "%")