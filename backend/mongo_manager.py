import datetime
from datetime import timedelta, datetime as dt2
import logging
import pymongo
from pymongo import MongoClient
import os
from backend import utility
from backend.errors import NoEnvValue

logger = logging.getLogger(__name__)

class BaseMongoManager: 
    client = None

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(BaseMongoManager, cls).__new__(cls, *args, **kwargs)
            cls._instance.client = None
        return cls._instance
    
    def connect(self, user_cluster: bool):
        if self.client:
            return
        
        s = "MONGO_CONN_STRING" if user_cluster else "MONGO_REPORTS_CONN_STRING"
        conn = os.getenv(s)
        
        if not conn:
            raise NoEnvValue(f"Environment variable {s} not found")

        self.client = MongoClient(conn)
        print(f"MongoDB connected with {s}!")

class MongoUserCluster(BaseMongoManager):
    def __init__(self):
        super().__init__()
        self.connect(user_cluster=True)        

    def __get_coll__(self):
        mydb = self.client["players_db"]
        mycol = mydb["players_collection"]
        return mycol

    def get_doc_from_eid(self, hashed_eid):
        return self.__get_coll__().find_one({"EID": hashed_eid})

    def upsert_user_doc(self, doc):
        logger.info(f"Upserting doc for hash {doc["EID"]}")
        self.__get_coll__().replace_one({"EID": doc["EID"]}, doc, upsert=True)
    
    def remove_old_users(self, days: int = 30):
        date_limit = utility.now_utc() - timedelta(days=days)
        self.__get_coll__().delete_many({'date_insert': {'$lt': date_limit}})

class MongoReportCluster(BaseMongoManager):
    def __init__(self):
        super().__init__()
        self.connect(user_cluster=False)

    def __get_coll__(self):
        mydb = self.client["reports"]
        mycol = mydb["reports_collection"]
        return mycol

