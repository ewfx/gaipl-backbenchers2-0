import os
import json
import requests
import PyPDF2
import io
import dotenv
import logging
from pymongo import MongoClient
from langchain.chains.summarize import load_summarize_chain
from flask import Flask, Response, request
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from crewai_tools import SerperDevTool
from langchain_weaviate import WeaviateVectorStore
import weaviate
from datetime import datetime
import textwrap
import tiktoken
from time import monotonic
from langchain.text_splitter import CharacterTextSplitter
from langchain.docstore.document import Document


dotenv.load_dotenv()

# Configuration
CONFIG = {
    "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
    "MONGO_URI": os.getenv("MONGO_URI"),
    "TELEMETRY_API": os.getenv("TELEMETRY_API"),
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

def fetch_incident_document(incident_id: str) -> dict:
    """Fetch incident details from MongoDB"""
    try:
        document = incident_collection.find_one({"incident_id": incident_id})
        if not document:
            logging.warning(f"Incident not found: {incident_id}")
        return document or {}
    except Exception as e:
        logging.error(f"Error fetching incident: {str(e)}")
        return {}

def fetch_kb_document(kb_article_id: str) -> dict:
    """Fetch KB document from MongoDB"""
    try:
        document = kb_collection.find_one({"article_id": kb_article_id})
        if not document:
            logging.warning(f"KB article not found: {kb_article_id}")
        return document or {}
    except Exception as e:
        logging.error(f"Error fetching KB article: {str(e)}")
        return {}

def read_pdf_from_url(url: str) -> str:
    """Read and summarize PDF content"""
    try:
        response = requests.get(url)
        pdf_file = io.BytesIO(response.content)
        text = ""
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        for page_num in range(min(3, len(pdf_reader.pages))):
            text += pdf_reader.pages[page_num].extract_text() or ""
        return text[:500]  # Return first 500 characters
    except Exception as e:
        logging.error(f"Error reading PDF: {str(e)}")
        return f"Error reading PDF: {str(e)}"

def make_telemetry_api_call(data: dict) -> dict:
    """Make telemetry API call"""
    try:
        response = requests.post(CONFIG["TELEMETRY_API"], json=data)
        return response.json()
    except Exception as e:
        logging.error(f"Telemetry API error: {str(e)}")
        return {"error": str(e)}

def send_email(to: str, subject: str, body: str) -> None:
    """Send notification email"""
    logging.info(f"Email sent to {to} - Subject: {subject}")
    # Implement actual email sending logic here
    print(f"Email notification:\nTo: {to}\nSubject: {subject}\nBody: {body}")


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


### 🚀 AI Agents with Logging (Add the new DecisionAgent)
def create_agent(role: str, goal: str, backstory: str) -> Agent:
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


classifier_task = Task(
    description="""
    Analyze the incident details, classify the issue type, and search Weaviate 
    to find relevant KB articles. Return the classification and top 3 KB article IDs.
    """,
    agent=classifier_agent,
    expected_output="""
    {
        "issue_type": "database_connection_error",
        "kb_article_ids": ["KB00001", "KB00042", "KB00123"],
        "confidence_scores": [0.92, 0.85, 0.78]
    }
    """
)

kb_article_task = Task(
    description="""
    Retrieve the full KB article details from MongoDB for the most relevant article ID.
    Verify the article exists and is applicable to the current incident.
    """,
    agent=kb_article_agent,
    expected_output="The complete KB article document from MongoDB"
)

decision_task = Task(
    description="""
    Analyze the KB article content and determine the appropriate workflow path.
    Decide which agents (PDF, API, or Workflow) should be executed next.
    """,
    agent=decision_agent,
    expected_output="""
    {
        "run_pdf_agent": true,
        "run_api_agent": false,
        "run_workflow_agent": true
    }
    """
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
# Execution Workflow
def execute_crew(incident_data: dict):
    """Execute the full incident resolution workflow"""
    context = {}
    incident_id = incident_data.get("incident_id")

    try:
        # 1. Fetch and validate incident
        incident = fetch_incident_document(incident_id)
        if not incident:
            yield json.dumps({"error": f"Incident {incident_id} not found"})
            return
        context["incident"] = incident

        # 2. Classify and find KB articles
        yield json.dumps({"agent": "Classifier", "status": "in_progress"})

        logging.info(" Adding the incident details to the context")
        search_query = f"{incident.get('title', '')} {incident.get('description', '')}"
        logging.info(" Search query: "+search_query)
        kb_results = search_kb_articles(search_query)
        logging.info(" KB results: "+str(kb_results))
        logging.info(incident)

        if not kb_results:
            yield json.dumps({"agent": "Classifier", "status": "failed", "reason": "No KB articles found"})
            yield from escalate_manually(context, "no_kb_articles_found")
            return

        context.update({
            "issue_type": classify_incident(incident),
            "kb_candidates": kb_results,
            "selected_kb": kb_results[0]["article_id"]
        })

        yield json.dumps({
            "agent": "Classifier",
            "status": "completed",
            "output": {
                "issue_type": context["issue_type"],
                "kb_articles": [kb["article_id"] for kb in kb_results]
            }
        })

        # 3. Retrieve KB article
        yield json.dumps({"agent": "KB Retriever", "status": "in_progress"})
        kb_article = fetch_kb_document(context["selected_kb"])

        if not kb_article:
            yield json.dumps({"agent": "KB Retriever", "status": "failed"})
            yield from try_kb_fallback(context, kb_results[1:])
            return

        context["kb_article"] = kb_article
        yield json.dumps({"agent": "KB Retriever", "status": "completed"})

        # 4. Determine workflow
        yield json.dumps({"agent": "Workflow Decider", "status": "in_progress"})
        decisions = analyze_kb_content(kb_article)
        context["decisions"] = decisions
        yield json.dumps({"agent": "Workflow Decider", "status": "completed", "output": decisions})

        # 5. Execute dynamic workflow
        if decisions.get("run_pdf_agent"):
            yield from process_pdf(context)

        if decisions.get("run_api_agent"):
            yield from process_api(context)

        if decisions.get("run_workflow_agent"):
            yield from process_workflow(context)

        # 6. Generate final summary
        yield json.dumps({"agent": "Report Generator", "status": "in_progress"})
        summary = generate_summary(context)
        yield json.dumps({"agent": "Report Generator", "status": "completed", "output": summary})

    except Exception as e:
        logging.error(f"Workflow error: {str(e)}")
        yield json.dumps({"error": str(e)})


# Helper execution functions
def analyze_kb_content(kb_article: dict) -> dict:
    """Analyze KB content to determine workflow"""
    content = kb_article.get("content", {})
    return {
        "run_pdf_agent": "manual_steps" in content,
        "run_api_agent": content.get("rest_api_details", {}).get("can_trigger_automatically", False),
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