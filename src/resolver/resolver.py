import base64
import re
import json
import requests
import PyPDF2
import io
import dotenv
import logging

from pinecone import Pinecone
from pymongo import MongoClient
from flask import Flask, Response, request
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from crewai_tools import SerperDevTool
import textwrap
import tiktoken
from time import monotonic
from langchain.text_splitter import CharacterTextSplitter
from langchain.docstore.document import Document
from langchain.chains.summarize import load_summarize_chain
from langchain_community.retrievers import PineconeHybridSearchRetriever
from pinecone_text.sparse import BM25Encoder
from langchain_huggingface import HuggingFaceEmbeddings
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
import os
from ssl import SSLError


dotenv.load_dotenv()

# Configuration
CONFIG = {
    "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
    "MONGO_URI": os.getenv("MONGO_URI"),
    "TELEMETRY_API": os.getenv("TELEMETRY_API"),
    "REST_API": os.getenv("REST_API"),
    "WEAVIATE_URL": os.getenv("WEAVIATE_URL"),
    "WEAVIATE_API_KEY": os.getenv("WEAVIATE_API_KEY"),
    "DATABASE_NAME": "IncidenceDB",
    "KB_COLLECTION": "ResolutionKnowledgeBase",
    "INCIDENT_COLLECTION": "Incidents",
    "LOG_PATH": os.path.abspath(os.path.join(os.path.dirname(__file__), "../logs/app.log"))
}

# Setup logging
os.makedirs(os.path.dirname(CONFIG["LOG_PATH"]), exist_ok=True)
logging.basicConfig(
    filename=CONFIG["LOG_PATH"],
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# Initialize Flask App
app = Flask(__name__)
llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo")

# Load OpenAI embeddings
embeddings = OpenAIEmbeddings()

# Database connections
try:
    mongo_client = MongoClient(os.getenv("MONGO_URI"))
    db = mongo_client[CONFIG["DATABASE_NAME"]]
    kb_collection = db[CONFIG["KB_COLLECTION"]]
    incident_collection = db[CONFIG["INCIDENT_COLLECTION"]]

    '''client = weaviate.connect_to_wcs(
        cluster_url=CONFIG["WEAVIATE_URL"],
        auth_credentials=weaviate.auth.AuthApiKey(api_key=CONFIG["WEAVIATE_API_KEY"])
    )

    # Create a Weaviate vector store
    vector_store = WeaviateVectorStore(
        client=client,
        index_name="Incident",
        text_key="description",  # Use the description field for search
        embedding=embeddings,  # Pass the embeddings object
    ) '''

except Exception as e:
    logging.error(f"Initialization error: {str(e)}")
    raise


# Helper Functions
def search_kb_articles(query: str, limit: int = 3) -> list:
    """Search for relevant KB articles using Weaviate vector database"""
    try:
        '''vector = embeddings.embed_query(query)
        results = client.query\
            .get("KnowledgeArticles", ["article_id", "title", "content"])\
            .with_near_vector({"vector": vector})\
            .with_limit(limit)\
            .do() '''
        #return results.get("data", {}).get("Get", {}).get("KnowledgeArticles", [])
        return ["KB0003"]
    except Exception as e:
        logging.error(f"Weaviate search error: {str(e)}")
        return []


def extract_kb_string(text: str) -> Optional[str]:
    """
    Extracts the first KB reference from text in various formats.
    Handles cases where KB reference might be adjacent to other text.

    Args:
        text: Input text to search for KB references

    Returns:
        str: The matched KB reference (format KB followed by digits) or None
    """
    # Match KB followed by digits, allowing for adjacent non-word characters
    match = re.search(r'(?:\b|_)KB(\d+)', text)

    if match:
        kb_ref = f"KB{match.group(1)}"
        # Pad with leading zeros to ensure 5 digits if needed
        if len(match.group(1)) < 5:
            kb_ref = f"KB{match.group(1).zfill(5)}"
        return kb_ref[:7]  # Return first 7 characters (KB + 5 digits)
    return None


def get_relevant_Kb_article(title, description):
    """
    Retrieves relevant KB articles using Pinecone hybrid search.

    Args:
        title (str): Incident title
        description (str): Incident description

    Returns:
        list: Relevant KB articles
    """


    # Load environment variables
    load_dotenv()

    # Configuration
    index_name = "hybrid-incident-search-langchain-pinecone"
    api_key = os.getenv("PINECONE_API_KEY")  # Always use environment variables for secrets

    try:
        # Initialize Pinecone client (new package)
        pc = Pinecone(api_key=api_key)

        # Get the existing index
        index = pc.Index(index_name)

        # Initialize embeddings and encoder
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        bm25_encoder = BM25Encoder().load("src/resolver/bm25_values.json")

        # Create retriever
        retriever = PineconeHybridSearchRetriever(
            embeddings=embeddings,
            sparse_encoder=bm25_encoder,
            index=index
        )

        # Combine title and description for better search
        query = f"{title}: {description}"

        # Retrieve results
        results = retriever.invoke(query)

        print("Extracted KB Document "+results.__getitem__(0).page_content)
        return extract_kb_string(results.__getitem__(0).page_content)

    except Exception as e:
        print(f"Error in KB article retrieval: {str(e)}")
        return []

# 🔹 Function to fetch Incident document from MongoDB
def fetch_incident_document(incident_id):
    logging.info(f"Fetching KB Incident for Incident ID: {incident_id}")
    try:
        document = incident_collection.find_one({"incident_id": incident_id})
        if document:
            logging.info("Incident document found. "+incident_id)
        else:
            logging.warning("Incident document not found. "+incident_id)
        return document or {}
    except Exception as e:
        logging.error(f"Error fetching Incident document: {str(e)}")
        return {}


# 🔹 Function to fetch KB document from MongoDB
def fetch_kb_document(kb_article_id):
    logging.info(f"Fetching KB document for Article ID: {kb_article_id}")
    try:
        #kb_article_id =  "KB00003"
        document = kb_collection.find_one({"article_id": kb_article_id})
        if document:
            logging.info("KB document found. "+kb_article_id)
        else:
            logging.warning("KB document not found. "+kb_article_id)
        return document or {}
    except Exception as e:
        logging.error(f"Error fetching KB document: {str(e)}")
        return {}


# 🔹 Function to call telemetry API
def make_telemetry_api_call(data):
    logging.info("Making Telemetry API call...")
    try:
        logging.info(data)
        response = requests.post(CONFIG["TELEMETRY_API"], json=data)
        response_json = response.json()
        logging.info("Telemetry API response received.")
        return response_json
    except requests.RequestException as e:
        logging.error(f"Telemetry API call failed: {str(e)}")
        return {"error": f"Telemetry API failed: {str(e)}"}

# 🔹 Function to call telemetry API
def make_rest_api_call(data):
    logging.info("Making REST API call...")
    try:
        logging.info(data)
        response = requests.post(CONFIG["REST_API"], json=data)
        response_json = response.json()
        logging.info("REST API response received.")
        return response_json
    except requests.RequestException as e:
        logging.error(f"REST API call failed: {str(e)}")
        return {"error": f"REST API failed: {str(e)}"}


def make_rest_api_call_with_url(url, data=None, jenkins_auth=True):
    """
    Make a REST API call with optional Jenkins authentication.

    Args:
        url (str): The API endpoint URL.
        data (dict, optional): JSON payload to send. Defaults to None.
        jenkins_auth (bool/str, optional): If True, uses default Jenkins auth.
                                          If string, uses it as auth token. Defaults to False.

    Returns:
        dict: API response or error message.
    """
    logging.info(f"Making REST API call to {url}")

    headers = {'Content-Type': 'application/json'}
    auth = None

    try:
        # Handle Jenkins authentication
        if jenkins_auth:
            if isinstance(jenkins_auth, str):
                # Use provided auth token directly
                token = os.getenv("JENKINS_AUTH_KEY")
                logging.info("Using provided Jenkins auth token")
                headers['Authorization'] = f"Basic {token}"
            else:
                # Use default Jenkins credentials from environment
                jenkins_user = os.getenv('JENKINS_USER')
                jenkins_token = os.getenv('JENKINS_TOKEN')

                if jenkins_user and jenkins_token:
                    logging.info("Using Jenkins credentials from environment")
                    credentials = f"{jenkins_user}:{jenkins_token}"
                    encoded_credentials = base64.b64encode(credentials.encode()).decode()
                    headers['Authorization'] = f"Basic {encoded_credentials}"
                else:
                    logging.warning("Jenkins auth requested but credentials are missing in the environment!")

        # Make the request
        logging.info(f"Request Headers: {headers}")
        response = requests.post(
            url,
            json=data,
            headers=headers,
            timeout=30
        )

        # Handle response
        response.raise_for_status()  # Raises exception for 4XX/5XX responses

        try:
            response_json = response.json()
            logging.info("REST API call successful")
            return response_json
        except ValueError:
            logging.info("API returned non-JSON response")
            final_url = url+"/"+os.getenv("JENKINS_BUILD_NUMBER")+"/job"
            return {"status": response.status_code, "content": final_url}

    except requests.RequestException as e:
        error_msg = f"REST API call failed: {str(e)}"
        logging.error(error_msg)
        return {
            "error": error_msg,
            "status_code": getattr(e.response, 'status_code', None),
            "details": str(e)
        }

'''
# 🔹 Function to read and summarize PDF content
def read_pdf_from_url(url):
    logging.info(f"Fetching PDF from URL: {url}")
    try:
        response = requests.get(url)
        pdf_file = io.BytesIO(response.content)

        text = ""
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        for page_num in range(min(3, len(pdf_reader.pages))):
            text += pdf_reader.pages[page_num].extract_text() or ""

        logging.info("PDF successfully read and summarized.")
        return text[:500]  # Return first 500 characters
    except Exception as e:
        logging.error(f"Error reading PDF: {str(e)}")
        return f"Error reading PDF: {str(e)}"
'''


# First install: pip install pymupdf
def read_pdf_from_url(url):
    logging.info(f"Fetching PDF from URL: {url}")
    try:
        # Convert GitHub blob URL to raw URL
        if 'github.com' in url and '/blob/' in url:
            url = url.replace('github.com', 'raw.githubusercontent.com').replace('/blob/', '/')

        headers = {
            'User-Agent': 'Mozilla/5.0',
            'Accept': 'application/pdf'
        }

        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        # Verify PDF content
        if not response.content.startswith(b'%PDF'):
            raise ValueError("URL does not point to a valid PDF file")

        with io.BytesIO(response.content) as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            for page in pdf_reader.pages[:3]:  # First 3 pages
                text += page.extract_text() or ""

        logging.info("PDF successfully read and summarized.")
        return text[:500]  # Return first 500 characters

    except Exception as e:
        logging.error(f"Error reading PDF: {str(e)}")
        return f"Error reading PDF: {str(e)}"
'''
# 🔹 Function to send an email
def send_email(to, subject, body):
    logging.info(f"Sending email to {to} with subject: {subject}")
    # Placeholder: Implement actual email sending logic
    print(f"Email sent to {to} | Subject: {subject} | Body: {body}")
'''

def send_email(to_email, subject, body):
    smtp_server = "localhost"
    smtp_port = 1025  # MailHog default SMTP port

    sender_email = "test@example.com"

    # Create email message
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        # Connect to MailHog SMTP server
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.sendmail(sender_email, to_email, msg.as_string())
        server.quit()
        print("✅ Email sent successfully via MailHog!")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")

def num_tokens_from_string(string: str, encoding_name: str) -> int:
    encoding = tiktoken.encoding_for_model(encoding_name)
    return len(encoding.encode(string))

def classify_incident(incident_details: dict) -> str:
    """Classify incident using LLM"""
    prompt = f"""
    Classify this incident based on:
    Title: {incident_details.get('title', '')}
    Description: {incident_details.get('description', '')}
    Possible categories: database, network, application, storage, security
    Return just the category name in lowercase.
    """
    model_name = "gpt-3.5-turbo"
    logging.info("Classification prompt: "+prompt)
    #logging.info("Classification prompt2 : "+llm.predict(prompt))

    num_tokens = num_tokens_from_string(prompt, model_name)
    logging.info(f"Input text has {num_tokens} tokens")

    text_splitter = CharacterTextSplitter.from_tiktoken_encoder(model_name=model_name)
    docs = [Document(page_content=t) for t in text_splitter.split_text(prompt)]
    gpt_35_turbo_max_tokens = 4097
    chain_type = "stuff" if num_tokens < gpt_35_turbo_max_tokens else "map_reduce"

    logging.info(f"Using summarization chain type: {chain_type}")
    chain = load_summarize_chain(llm, chain_type=chain_type, prompt=prompt, verbose=True)

    start_time = monotonic()

    summary = chain.run(docs)
    execution_time = monotonic() - start_time
    logging.info(f"Summarization completed in {execution_time:.2f} seconds")

    # Remove newlines and extra spaces
    cleaned_summary = " ".join(summary.replace("\n", " ").split())

    return textwrap.fill(cleaned_summary, width=100)


### 🚀 AI Agents with Logging

def create_agent(role, goal, backstory):
    return Agent(
        role=role,
        goal=goal,
        backstory=backstory,
        llm=llm,
        memory=True,
        verbose=True,
        allow_delegation=False,
        max_iter=10,
        tools=[SerperDevTool()]
    )


classifier_agent = create_agent(
    "Incident Classifier",
    "Classify incidents and find relevant KB articles",
    "Expert in analyzing incidents and retrieving knowledge base solutions"
)

kb_article_agent = create_agent(
    "KB Retriever",
    "Retrieve KB articles from database",
    "Specialized in knowledge base retrieval and analysis"
)

### 🚀 AI Agents with Logging (Add the new DecisionAgent)
decision_agent = create_agent(
    "Workflow Decider",
    "Determine the appropriate workflow path",
    "Expert in analyzing KB content and making execution decisions"
)

pdf_agent = create_agent(
    "PDF Analyzer",
    "Extract information from PDF documents",
    "Skilled in reading and summarizing technical documents"
)

api_agent = create_agent(
    "API Handler",
    "Execute API calls when needed",
    "Specialized in API integrations and automation"
)

telemetry_agent = create_agent(
    "Telemetry Analyst",
    "Analyze system telemetry data",
    "Expert in interpreting system metrics and logs"
)

workflow_agent = create_agent(
    "Workflow Manager",
    "Handle manual escalation workflows",
    "Experienced in incident escalation procedures"
)

summary_agent = create_agent(
    "Report Generator",
    "Create comprehensive incident reports",
    "Skilled in compiling and presenting technical information"
)

### 🔹 AI Tasks

def create_task(description, agent):
    return Task(
        description=description,
        agent=agent,
        expected_output=f"Executed: {description}"
    )


classifier_task = create_task("Analyze incident and classify issue type.", classifier_agent)
kb_article_task = create_task("Retrieve KB article ID from MongoDB.", kb_article_agent)
### 🔹 AI Tasks (Add the new DecisionTask)
decision_task = create_task(
    "Analyze KB article content and determine next steps",
    decision_agent
)
pdf_task = create_task("Summarize PDF document from KB article.", pdf_agent)
api_task = create_task("Check KB settings and decide API trigger.", api_agent)
telemetry_task = create_task("Fetch telemetry data for affected services.", telemetry_agent)
workflow_task = create_task("Trigger manual escalation if required.", workflow_agent)
summary_task = create_task("Compile results and generate structured summary.", summary_agent)

### 🏗️ CrewAI Configuration
crew = Crew(
    agents=[classifier_agent, kb_article_agent,decision_agent,  pdf_agent, api_agent, telemetry_agent, workflow_agent, summary_agent],
    tasks=[classifier_task, kb_article_task, decision_task, pdf_task, api_task, telemetry_task, workflow_task, summary_task],
    process=Process.sequential,
    verbose=True
)


# 🚀 Updated Execution function with dynamic workflow
def execute_crew(incident_data):
    logging.info(f"Executing CrewAI workflow for Incident: {incident_data.get('incident_id')}")
    context = {}  # Store execution context

    try:
        incident_id = incident_data.get("incident_id")
        incident = fetch_incident_document(incident_id)
        if not incident:
            yield json.dumps({"error": f"Incident {incident_id} not found"})
            return
        context["incident"] = incident
        # 1. Classify the issue
        yield json.dumps({"agent": "Classifier", "status": "in_progress", "output": "Classifying issue..."})
        issue_type = llm.predict(f"Classify the issue: {incident_data}")
        context["issue_type"] = issue_type
        yield json.dumps({"agent": "Classifier", "status": "completed", "output": f"Issue type: {issue_type}"})

        # 2. Fetch KB article
        yield json.dumps({"agent": "KB Article Retriever", "status": "in_progress", "output": "Fetching KB Article..."})
        kb_article_id = get_relevant_Kb_article(incident_data.get("title"), incident_data.get("description"))
        kb_article = fetch_kb_document(kb_article_id)
        context["kb_article"] = kb_article

        if not kb_article:
            yield json.dumps({"agent": "KB Article Retriever", "status": "skipped", "output": "No KB Article found"})
            logging.warning("No KB Article found. Escalating manually.")

            yield json.dumps({"agent": "Workflow Manager", "status": "in_progress", "output": "Escalating manually..."})
            email_body = f"Incident: {incident_data}\nIssue Type: {issue_type}\nKB Article Missing"
            send_email("vikas.tirumalla@gmail.com", "Escalation Required", email_body)
            yield json.dumps({"agent": "Workflow Manager", "status": "completed", "output": "Escalation email sent"})

            # Generate final summary
            yield json.dumps({"agent": "Summary Generator", "status": "in_progress", "output": "Generating summary..."})
            summary = {"issue_type": issue_type, "resolution": "manual_escalation"}
            yield json.dumps({"agent": "Summary Generator", "status": "completed", "output": summary})
            return

        yield json.dumps({"agent": "KB Article Retriever", "status": "completed", "output": f"Found KB: {kb_article.get('article_id')}"})

        # 3. Decision Agent - Analyze KB content
        yield json.dumps({"agent": "Workflow Decision Agent", "status": "in_progress", "output": "Analyzing KB content to trigger Workflow..."})

        content = kb_article.get("content", {})
        decisions = {
            "run_pdf_agent": "manual_steps" in content,
            "run_api_agent": content.get("rest_api_details", {}).get("can_trigger_automatically", False),
            "run_telemetry_agent": content.get("monitoring_details", {}).get("enabled", False),
            "run_workflow_agent": content.get("workflow", {}).get("enabled", False)
        }
        context["decisions"] = decisions
        yield json.dumps({
            "agent": "Workflow Decision Agent",
            "status": "completed",
            "output": decisions
        })

        # 4. Execute dynamic workflow based on decisions
        if decisions["run_pdf_agent"]:
            yield json.dumps({"agent": "PDF Reader", "status": "in_progress", "output": "Processing PDF..."})
            pdf_url = content["manual_steps"]["file_url"]
            #pdf_summary = read_pdf_from_url(pdf_url)
            context["pdf_summary"] = pdf_url
            yield json.dumps({"agent": "PDF Reader", "status": "completed", "output": pdf_url})

        if decisions["run_api_agent"]:
            yield json.dumps({"agent": "API Handler", "status": "in_progress", "output": "Triggering API..."})
            #api_response = make_rest_api_call(content["rest_api_details"]["payload"])
            api_response = make_rest_api_call_with_url(content["rest_api_details"]["url"], content["rest_api_details"]["payload"])
            context["api_response"] = api_response
            yield json.dumps({"agent": "API Handler", "status": "completed", "output": api_response})

        if decisions["run_telemetry_agent"]:
            yield json.dumps({"agent": "Telemetry API Handler", "status": "in_progress", "output": "Triggering Telemetry API for all the dependent apps..."})
            #logging.info(content["monitoring_details"]["nodes_to_monitor"]["node_id"])
            #logging.info(print(content["monitoring_details"]["nodes_to_monitor"]))
            #logging.info(print(type(content["monitoring_details"]["nodes_to_monitor"])))
            api_response = make_telemetry_api_call(content["monitoring_details"]["nodes_to_monitor"])
            context["api_response"] = api_response
            yield json.dumps({"agent": "Telemetry API Handler", "status": "completed", "output": api_response})

        logging.warning("about to run workflow agent.")
        print("about to run workflow agent")
        if decisions["run_workflow_agent"]:
            yield json.dumps({"agent": "Workflow Manager", "status": "in_progress", "output": "Initiating workflow..."})

            logging.warning("running workflow agent.")
            print("running workflow agent")
            # Get the email template from KB article content
            logging.info( content)
            print( content)
            logging.info(content["workflow"])
            print(content["workflow"])
            email_template = content["workflow"]["email_template"]
            template_vars = email_template["metadata"]["variables"]

            logging.info(email_template)
            print(email_template)
            logging.info(template_vars)
            # Get incident details from context
            incident = context.get("incident", {})

            # Create variable mapping with actual incident values
            replacements = {
                "{{TICKET_ID}}": incident.get("incident_id", incident_id),
                "{{TEAM_NAME}}": incident.get("assigned_team", "Dev team"),
                "{{APPLICATION_NAME}}": incident.get("application", incident_data.get("affected_microservice")),
                "{{ISSUE_DESCRIPTION}}": incident.get("description", incident_data.get("description")),
                "{{IMPACT}}": incident.get("impact", incident_data.get("priority")),
                "{{PRIORITY}}": incident.get("priority", incident_data.get("priority")),
                "{{REQUESTED_ACTION}}": "Please investigate and resolve according to KB article " + kb_article_id,
                "{{DEADLINE}}": (datetime.now() + timedelta(hours=4)).strftime("%Y-%m-%d %H:%M"),
                "{{YOUR_NAME}}": "Automated Incident Management",
                "{{YOUR_ROLE}}": "Workflow Automation",
                "{{CONTACT_INFO}}": "incident-support@company.com",
                "{{TIMESTAMP}}": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

            # Replace placeholders in email subject and body
            email_subject = email_template["subject"]
            email_body = email_template["body"]

            logging.info(email_body)
            logging.info(email_subject)
            for placeholder, value in replacements.items():
                email_subject = email_subject.replace(placeholder, str(value))
                email_body = email_body.replace(placeholder, str(value))

            # Get recipient from workflow steps or use default
            recipient = "support@example.com"
            if "recipient" in content["workflow"]:
                recipient = content["workflow"]["recipient"]

            # Send the email
            send_email(
                to_email=recipient,
                subject=email_subject,
                body=email_body
            )

            workflow_result = {
                "status": "completed",
                "action": "escalation_email_sent",
                "recipient": recipient,
                "template_used": kb_article_id,
                "timestamp": datetime.now().isoformat()
            }

            context["workflow_result"] = workflow_result
            yield json.dumps({
                "agent": "Workflow Manager",
                "status": "completed",
                "output": workflow_result
            })

        # 5. Generate final summary
        yield json.dumps({"agent": "Summary Generator", "status": "in_progress", "output": "Compiling results..."})
        summary = {
            "issue_type": context["issue_type"],
            "kb_article_id": context["kb_article"].get("article_id"),
            "actions_taken": context["decisions"],
            "results": {
                "pdf_summary": context.get("pdf_summary"),
                "api_response": context.get("api_response"),
                "workflow_result": context.get("workflow_result")
            }
        }
        yield json.dumps({"agent": "Summary Generator", "status": "completed", "output": summary})

        logging.info(f"Incident {incident_data.get('incident_id')} processed successfully.")

    except Exception as e:
        logging.error(f"Error during execution: {str(e)}")
        yield json.dumps({"error": str(e)})


'''
# Helper execution functions
def analyze_kb_content(kb_article: dict) -> dict:
    """Analyze KB content to determine workflow"""
    content = kb_article.get("content", {})
    return {
        "run_pdf_agent": "manual_steps" in content,
        "run_api_agent": content.get("rest_api_details", {}).get("can_trigger_automatically", False),
        "run_telemetry_agent": content.get("monitoring_details", {}),
        "run_workflow_agent": content.get("workflow", {}).get("enabled", False)
    }


def process_pdf(context: dict):
    """Execute PDF processing workflow"""
    yield json.dumps({"agent": "PDF Analyzer", "status": "in_progress"})
    pdf_url = context["kb_article"]["content"]["manual_steps"]["file_url"]
    summary = read_pdf_from_url(pdf_url)
    context["pdf_summary"] = summary
    yield json.dumps({"agent": "PDF Analyzer", "status": "completed", "output": summary[:200] + "..."})


def process_api(context: dict):
    """Execute API workflow"""
    yield json.dumps({"agent": "API Handler", "status": "in_progress"})
    payload = context["kb_article"]["content"]["rest_api_details"]["payload"]
    response = make_telemetry_api_call(payload)
    context["api_response"] = response
    yield json.dumps({"agent": "API Handler", "status": "completed", "output": response})


def process_workflow(context: dict):
    """Execute manual workflow"""
    yield json.dumps({"agent": "Workflow Manager", "status": "in_progress"})
    steps = context["kb_article"]["content"]["workflow"]["steps"]
    # Process workflow steps
    result = f"Executed {len(steps)} workflow steps"
    context["workflow_result"] = result
    yield json.dumps({"agent": "Workflow Manager", "status": "completed", "output": result})


def escalate_manually(context: dict, reason: str):
    """Handle manual escalation"""
    email_body = f"""
    Incident: {context.get('incident', {})}
    Issue Type: {context.get('issue_type', 'unknown')}
    Reason: {reason}
    """
    send_email("support@example.com", "Escalation Required", email_body)
    yield json.dumps({"agent": "Workflow Manager", "status": "completed", "output": "Escalation email sent"})

    summary = {
        "issue_type": context.get("issue_type"),
        "resolution": "manual_escalation",
        "reason": reason
    }
    yield json.dumps({"agent": "Report Generator", "status": "completed", "output": summary})


def try_kb_fallback(context: dict, fallback_kbs: list):
    """Try fallback KB articles"""
    for kb in fallback_kbs:
        kb_article = fetch_kb_document(kb["article_id"])
        if kb_article:
            context["kb_article"] = kb_article
            context["selected_kb"] = kb["article_id"]
            yield json.dumps(
                {"agent": "KB Retriever", "status": "completed", "output": f"Using fallback KB: {kb['article_id']}"})
            return

    yield from escalate_manually(context, "no_valid_kb_articles")


def generate_summary(context: dict) -> dict:
    """Generate final summary report"""
    return {
        "incident_id": context["incident"].get("incident_id"),
        "issue_type": context.get("issue_type"),
        "kb_article": context.get("selected_kb"),
        "actions": context.get("decisions", {}),
        "results": {
            "pdf_summary": context.get("pdf_summary"),
            "api_response": context.get("api_response"),
            "workflow_result": context.get("workflow_result")
        },
        "timestamp": datetime.now().isoformat()
    }

'''