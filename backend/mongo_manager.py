import datetime
from datetime import timedelta, datetime as dt2
import pymongo
from pymongo import MongoClient
import os
from backend.errors import NoEnvValue

class mongo_manager:

    client = None

    def __init__(self):
        if self.client:
            return
        
        conn = os.getenv('MONGO_CONN_STRING')
        if not conn:
            raise NoEnvValue("MONGO_CONN_STRING") 

        self.client = MongoClient(conn)

    def __get_coll__(self):
        mydb = self.client["players_db"]
        mycol = mydb["players_collection"]
        return mycol

    def get_doc_from_eid(self, hashed_eid):
        return self.__get_coll__().find_one({"EID": hashed_eid})

    def upsert_user_doc(self, doc):
        self.__get_coll__().replace_one({"EID": doc["EID"]}, doc, upsert=True)

