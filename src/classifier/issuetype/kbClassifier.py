import os
import pickle
import logging

# Define paths
MODEL_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../models/kb_model.pkl"))
LOG_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../logs/app.log"))

# Configure logging
logging.basicConfig(filename=LOG_PATH, level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Load the trained model
with open(MODEL_PATH, 'rb') as f:
    model_data = pickle.load(f)

model = model_data['model']
vectorizer = model_data['vectorizer']
label_encoder = model_data['label_encoder']


def predict_knowledgeBaseArticle(title, description):
    """Predict the affected microservice based on title and description."""
    text_input = title + " " + description
    text_vectorized = vectorizer.transform([text_input])
    prediction = model.predict(text_vectorized)
    kb_article_id = label_encoder.inverse_transform(prediction)[0]

    logging.info(
        f"Prediction made: title={title}, description={description}, kb_article_id={kb_article_id}")

    return kb_article_id


def get_relevant_Kb_article(title, description):
    from langchain_community.retrievers import PineconeHybridSearchRetriever
    from pinecone import Pinecone, ServerlessSpec
    from pinecone_text.sparse import BM25Encoder
    from langchain_huggingface import HuggingFaceEmbeddings
    import re
    from dotenv import load_dotenv
    load_dotenv()

    index_name = "hybrid-incident-search-langchain-pinecone"
    api_key = "pcsk_6mJ6zv_4R7GU4WBdDtDxFJ6d8houRws7xH9TPuoSd8J5ijfuKtWk8c3R8rAVPUwHNs3sYW"

    ## initialize the Pinecone client
    pc = Pinecone(api_key=api_key)

    # create the index
    index = pc.Index(index_name)

    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    bm25_encoder = BM25Encoder().load("bm25_values.json")

    retriever = PineconeHybridSearchRetriever(embeddings=embeddings, sparse_encoder=bm25_encoder, index=index)

    result = retriever.invoke("issue with auth service")
    return result

