import os
import textwrap
import pandas as pd
import tiktoken
import dotenv
import logging
from time import monotonic
from langchain.chains.summarize import load_summarize_chain
from langchain.docstore.document import Document
from langchain.text_splitter import CharacterTextSplitter
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate

# Load environment variables
dotenv.load_dotenv()

# Constants
#DATA_FILE_PATH = "../../data/data_1000.txt"
#CSV_FILE_PATH = "../../data/data_1000.csv"
CSV_FILE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/data_1000.csv"))
DATA_FILE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/data_1000.txt"))
LOG_FILE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../logs/app.log"))

# Ensure log directory exists
os.makedirs(os.path.dirname(LOG_FILE_PATH), exist_ok=True)

# Configure logging
logging.basicConfig(
    filename=LOG_FILE_PATH,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# Load OpenAI API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Define model
model_name = "gpt-3.5-turbo"
llm = ChatOpenAI(temperature=0, model_name=model_name)

# Function to count tokens
def num_tokens_from_string(string: str, encoding_name: str) -> int:
    encoding = tiktoken.encoding_for_model(encoding_name)
    return len(encoding.encode(string))

# Function to summarize a given text
def summarize_text(input_text):
    logging.info("Summarization request received.. "+input_text)

    prompt_template = """Write a concise summary of the following:
                         {text}
                         CONCISE SUMMARY IN 50 words:"""
    prompt = PromptTemplate(template=prompt_template, input_variables=["text"])

    num_tokens = num_tokens_from_string(input_text, model_name)
    logging.info(f"Input text has {num_tokens} tokens")

    text_splitter = CharacterTextSplitter.from_tiktoken_encoder(model_name=model_name)
    docs = [Document(page_content=t) for t in text_splitter.split_text(input_text)]

    gpt_35_turbo_max_tokens = 4097
    chain_type = "stuff" if num_tokens < gpt_35_turbo_max_tokens else "map_reduce"

    logging.info(f"Using summarization chain type: {chain_type}")
    chain = load_summarize_chain(llm, chain_type=chain_type, prompt=prompt, verbose=True)

    start_time = monotonic()
    try:
        summary = chain.run(docs)
        execution_time = monotonic() - start_time
        logging.info(f"Summarization completed in {execution_time:.2f} seconds")

        # Remove newlines and extra spaces
        cleaned_summary = " ".join(summary.replace("\n", " ").split())

        return {
            "summary": textwrap.fill(cleaned_summary, width=100),
            "tokens": num_tokens,
            "chain_type": chain.__class__.__name__,
            "run_time": execution_time
        }
    except Exception as e:
        logging.error(f"Summarization error: {str(e)}")
        return {"error": "Summarization failed"}

# Function to get incident details from CSV and summarize them
def summarize_incident(incident_id):
    logging.info(f"Fetching details for Incident ID: {incident_id}")

    try:
        logging.info("File path "+CSV_FILE_PATH)
        df = pd.read_csv(CSV_FILE_PATH)
        incident = df[df["incident_id"] == incident_id]

        if incident.empty:
            logging.warning(f"Incident ID {incident_id} not found")
            return {"error": "Incident ID not found"}

        # Select relevant columns
        columns_to_include = ["title", "description", "affected_app"]
        selected_data = incident[columns_to_include].to_string(index=False)

        logging.info(f"Incident details extracted, summarizing now...")
        return summarize_text(selected_data)

    except Exception as e:
        logging.error(f"Error fetching incident details: {str(e)}")
        return {"error": str(e)}
