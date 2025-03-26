import os
import logging
import pandas as pd
import pickle
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report

# Define paths
DATA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../data/data_1000.csv"))
MODEL_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../models/kb_model.pkl"))
LOG_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../logs/training.log"))

# Configure logging
logging.basicConfig(filename=LOG_PATH, level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logging.info("Starting KB model training...")

# Load dataset
df = pd.read_csv(DATA_PATH)

# Preprocess data
df['combined_feature'] = df['title'].astype(str) + " " + df['description'].astype(str)
X = df['combined_feature']
y = df['kb_article_id']

# Convert text data to numerical vectors using TF-IDF
vectorizer = TfidfVectorizer(max_features=5000, stop_words='english')
X_tfidf = vectorizer.fit_transform(X)

# Encode labels
label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y)

# Split dataset
X_train, X_test, y_train, y_test = train_test_split(X_tfidf, y_encoded, test_size=0.2, random_state=42)

# Train model
model = LogisticRegression(multi_class='multinomial', solver='lbfgs', max_iter=1000)
model.fit(X_train, y_train)

# Evaluate model
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
logging.info(f"Model Accuracy: {accuracy:.2f}")
#logging.info("Classification Report:\n" + classification_report(y_test, y_pred, target_names=label_encoder.classes_))

# Save model & vectorizer
with open(MODEL_PATH, 'wb') as f:
    pickle.dump({'model': model, 'vectorizer': vectorizer, 'label_encoder': label_encoder}, f)

logging.info(f"Model saved at: {MODEL_PATH}")
print(f"Model training complete. Accuracy: {accuracy:.2f}")
