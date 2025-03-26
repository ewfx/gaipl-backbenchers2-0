from pymongo import MongoClient, DESCENDING
import json
from datetime import datetime
from bson import json_util

client = MongoClient("mongodb+srv://visuads:gqmlYmwxYRCCDAyB@incidencedb.4jkra.mongodb.net/?retryWrites=true&w=majority")  # Change if using a remote DB
db = client["IncidenceDB"]
collection = db["Comments"]

def getComments(requestJSON):
   
    filter={};
    if requestJSON is not None or requestJSON == {}:
       addFilters(requestJSON,'incident_id',filter)
    data = collection.find(filter).sort('date',DESCENDING)
    documents = list(data)
    json_data = json.dumps(documents, default=json_util.default)
    return json_data

def saveComments(comment):
    collection.insert_one(comment)
    return 'success';

def addFilters(requestJSON,key,filter):
    value=requestJSON.get(key, None) ;
    print(value)
    if value is not None and value != '':
        filter[key]=value;





