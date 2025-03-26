
# **Local Setup & Runbook**

## **1️⃣ Local Setup Instructions**

### **📌 Prerequisites**
Ensure you have the following installed:
- **Python 3.12+** → [Download Python](https://www.python.org/downloads/) < 3.13
- **pip** (comes with Python)
- **Virtual Environment (venv)**
- **Postman** (for API testing, optional)

### **📂 Clone the Repository & Navigate to Project**
```sh
git clone [https://github.com/backbenchers2point0/AIEnabled-Integrated-Platform-Environment.git](https://github.com/ewfx/gaipl-backbenchers2-0.git)
```

### **📦 Create & Activate Virtual Environment**
```sh
conda create -p venv python==3.12.0 -y
conda activate {absolutePath}/venv
venv\Scripts\activate    # On Windows
```

### **📥 Install Dependencies**
```sh
pip install -r requirements.txt
```

### **📥 Train Data**
```sh
python src/classifier/microservice-classifier/train_and_save.p
```

### **🔧 Configure Environment Variables**
Create a `.env` file inside the project root and add required configurations:
```ini
# Example .env file
MONGO_URI=mongodb://localhost:27017/
OPENAI_API_KEY=your_openai_key
TELEMETRY_API=http://localhost:5000/telemetry
```

### **🚀 Running the Application**
```sh
python src/run.py
```

### **📌 Running in Docker (If Required)**
```sh
docker build -t my-app .
docker run -p 5000:5000 my-app
```

### **🔍 Testing API Endpoints**
Using **Postman** or `curl`:
```sh
curl -X GET http://localhost:5001/api/health
```

### **🔍 Setting up Jenkins in local**
1. Download Jenkins from [here](https://www.jenkins.io/download/)
2. Download Apache Tomcat from [here](https://tomcat.apache.org/download-90.cgi)
3. Place the Jenkins war file in the webapps folder of Tomcat and start the server

catalina.sh start
---

### **🔍 Setting up MailHog in local**

brew install mailhog

To start the server run below command
mailhog

---

## **2️⃣ Runbook: Operating & Troubleshooting**

### **🟢 Starting the Application**
1. Activate the virtual environment: `source venv/bin/activate`
2. Run the application: `python src/run.py`
3. Verify it’s running: `curl http://localhost:5001/api/health`

### **🛑 Stopping the Application**
1. Press `CTRL+C` if running in terminal

### **📊 Monitoring Logs**
```sh
tail -f logs/app.log
```

### **🚨 Troubleshooting**
| Issue | Solution |
|--------|----------|
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` |
| `.env not found` | Create `.env` file as per example above |
| `Address already in use` | Kill process using `lsof -i :5000` and restart |


## **✅ Conclusion**
Following these steps ensures a smooth local setup and troubleshooting. For any persistent issues, check logs (`logs/app.log`) or restart the environment.

📌 **For more details, refer to the `docs/` directory!**

