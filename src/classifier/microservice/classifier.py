import os
import pickle
import logging

# Define paths
MODEL_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../models/microservice_model.pkl"))
LOG_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../logs/app.log"))

# Configure logging
logging.basicConfig(filename=LOG_PATH, level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Load the trained model
with open(MODEL_PATH, 'rb') as f:
    model_data = pickle.load(f)

model = model_data['model']
vectorizer = model_data['vectorizer']
label_encoder = model_data['label_encoder']


def predict_microservice(title, description):
    """Predict the affected microservice based on title and description."""
    text_input = title + " " + description
    text_vectorized = vectorizer.transform([text_input])
    prediction = model.predict(text_vectorized)
    predicted_microservice = label_encoder.inverse_transform(prediction)[0]

    logging.info(
        f"Prediction made: title={title}, description={description}, predicted_microservice={predicted_microservice}")

    return predicted_microservice
