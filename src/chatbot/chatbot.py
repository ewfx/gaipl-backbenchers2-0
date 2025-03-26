from flask import Flask, request, jsonify
from langchain_community.retrievers import PineconeHybridSearchRetriever
from pinecone import Pinecone
from pinecone_text.sparse import BM25Encoder
from langchain_huggingface import HuggingFaceEmbeddings
import os
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Load environment variables
load_dotenv()


class HybridSearchRetriever:
    def __init__(self):
        self.index_name = "hybrid-incident-search-langchain-pinecone"
        self.api_key = os.getenv("PINECONE_API_KEY")
        self.initialize_components()

    def initialize_components(self):
        """Initialize all required components for hybrid search"""
        try:
            # Initialize Pinecone client
            self.pc = Pinecone(api_key=self.api_key)

            # Verify index exists
            if self.index_name not in self.pc.list_indexes().names():
                raise ValueError(f"Index {self.index_name} not found")

            self.index = self.pc.Index(self.index_name)

            # Initialize embeddings
            self.embeddings = HuggingFaceEmbeddings(
                model_name="all-MiniLM-L6-v2",
                model_kwargs={'device': 'cpu'}
            )

            # Load BM25 encoder
            self.bm25_encoder = BM25Encoder().load("src/resolver/bm25_values.json")

            # Create retriever
            self.retriever = PineconeHybridSearchRetriever(
                embeddings=self.embeddings,
                sparse_encoder=self.bm25_encoder,
                index=self.index,
                top_k=5
            )

        except Exception as e:
            logging.error(f"Initialization failed: {str(e)}")
            raise

    def search(self, query: str) -> list:
        """Perform hybrid search and return documents with KB references"""
        try:
            results = self.retriever.invoke(query)
            return [
                {
                    "content": doc.page_content,
                    "metadata": doc.metadata
                }
                for doc in results
            ]
        except Exception as e:
            logging.error(f"Search failed: {str(e)}")
            return []

