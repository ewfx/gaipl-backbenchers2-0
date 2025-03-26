from pymongo import MongoClient, DESCENDING
import json
from datetime import datetime
from bson import json_util

client = MongoClient("mongodb+srv://visuads:gqmlYmwxYRCCDAyB@incidencedb.4jkra.mongodb.net/?retryWrites=true&w=majority")  # Change if using a remote DB
db = client["IncidenceDB"]


def getIncidenceDate(requestJSON,pageSize,pageNo):
    collection = db["Incidents"]
    skip = (pageNo - 1) * pageSize
    filter={};
    if requestJSON is not None or requestJSON == {}:
       addFilters(requestJSON,'incident_id',filter)
       addFilters(requestJSON,'priority',filter)
       addFilters(requestJSON,'status',filter)
       addDateRangeFilter(requestJSON.get('fromDate', None),requestJSON.get('toDate', None),'reported_date',filter)
    print(filter)
    if filter is not None or filter != {}:
         data = collection.find(filter).skip(skip).limit(pageSize).sort('reported_date',DESCENDING)
    else:
        data = collection.find().skip(skip).limit(pageSize).sort('reported_date',DESCENDING)
    documents = list(data)
    json_data = json.dumps(documents, default=json_util.default)
    return json_data

def addFilters(requestJSON,key,filter):
    value=requestJSON.get(key, None) ;
    print(value)
    if value is not None and value != '':
        filter[key]=value;



def addDateRangeFilter(startDate,endDate,key,filter):
    if startDate is not None and startDate != '' and endDate is not None and endDate != '' :
        start_date = datetime.strptime(startDate, "%d-%m-%Y").date()
        end_date = datetime.strptime(endDate, "%d-%m-%Y").date()
        #start_date = datetime(2023, 3, 1)  # Example: March 1, 2023
        #end_date = datetime(2025, 3, 31)
        filter[key]={"$gte": datetime.combine(start_date, datetime.min.time()), "$lte": datetime.combine(end_date, datetime.min.time())}

def updateIncident(record):
    collection = db["Incidents"]
    query={'incident_id':record.incident_id}
    collection.replace_one(query,record)
    return 'success';
