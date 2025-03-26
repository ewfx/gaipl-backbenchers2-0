from langchain_community.retrievers import PineconeHybridSearchRetriever
from pinecone import Pinecone,ServerlessSpec
from pinecone_text.sparse import BM25Encoder
from langchain_huggingface import HuggingFaceEmbeddings
import re
from dotenv import load_dotenv
load_dotenv()
import os

index_name="hybrid-incident-search-langchain-pinecone"


from langchain_community.retrievers import PineconeHybridSearchRetriever

import os
from pinecone import Pinecone,ServerlessSpec
## initialize the Pinecone client
pc=Pinecone(api_key="pcsk_6mJ6zv_4R7GU4WBdDtDxFJ6d8houRws7xH9TPuoSd8J5ijfuKtWk8c3R8rAVPUwHNs3sYW")

#create the index
if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=384,  # dimensionality of dense model
        metric="dotproduct",  # sparse values supported only for dotproduct
        spec=ServerlessSpec(cloud="aws", region="us-east-1"),
    )


index=pc.Index(index_name)
print(index)

## vector embedding and sparse matrix
import os
from dotenv import load_dotenv
load_dotenv()

#os.environ["HF_TOKEN"]=os.getenv("HF_TOKEN")

from langchain_huggingface import HuggingFaceEmbeddings
embeddings=HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
print(embeddings)

from pinecone_text.sparse import BM25Encoder

bm25_encoder=BM25Encoder().default()
print(bm25_encoder)


sentences=[
     "IncidentID: INC844121 Title Failed transactions in Payment Service Description Transactions in Payment Service are failing due to database issues. kb_article_id KB00001",
        "IncidentID: INC765698 Title Database deadlock in Notification Service Description API requests to Notification Service are failing with 500 errors. kb_article_id KB00004",
        "IncidentID: INC111135 Title Failed transactions in Database B Description Transactions in Database B are failing due to database issues. kb_article_id KB00003",
        "IncidentID: INC679492 Title Notification failure in Auth Service Description Auth Service is unresponsive, causing service degradation. kb_article_id KB00002",
         "IncidentID: INC652605 Title Payment Service connection timeout Description API requests to Payment Service are failing with 500 errors. kb_article_id KB00005"

]

## tfidf values on these sentence
bm25_encoder.fit(sentences)

## store the values to a json file
bm25_encoder.dump("bm25_values.json")

# load to your BM25Encoder object
bm25_encoder = BM25Encoder().load("bm25_values.json")

retriever=PineconeHybridSearchRetriever(embeddings=embeddings,sparse_encoder=bm25_encoder,index=index)

retriever.add_texts(
    [
        "IncidentID: INC844121 Title Failed transactions in Payment Service Description Transactions in Payment Service are failing due to database issues. kb_article_id KB00001",
        "IncidentID: INC765698 Title Database deadlock in Notification Service Description API requests to Notification Service are failing with 500 errors. kb_article_id KB00004",
        "IncidentID: INC111135 Title Failed transactions in Database B Description Transactions in Database B are failing due to database issues. kb_article_id KB00003",
        "IncidentID: INC679492 Title Notification failure in Auth Service Description Auth Service is unresponsive, causing service degradation. kb_article_id KB00002",
        "IncidentID: INC652605 Title Payment Service connection timeout Description API requests to Payment Service are failing with 500 errors. kb_article_id KB00005"

]
)

retriever.invoke("What city did i visit first")