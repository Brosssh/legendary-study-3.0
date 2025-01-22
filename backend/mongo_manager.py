from collections import OrderedDict
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
        logger.info(f"Initialized MongoDB cluster for {s}!")


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
        self.__get_coll__().delete_many({"date_insert": {"$lt": date_limit}})

    def process_zlc_record(self) -> int:
        pipeline = [
            {
                "$match": {
                    "cheater": False,
                    f"ships_count.{utility.ZLC_SHIP}": {"$exists": True, "$gt": 0},
                    "leg_arti_list": {"$size": 0},
                }
            },
            {"$sort": {f"ships_count.{utility.ZLC_SHIP}": -1}},
            {"$limit": 1},
        ]
        logger.info("Starting query for zlc_record")
        doc_result = next(self.__get_coll__().aggregate(pipeline), None)
        return doc_result["ships_count"][utility.ZLC_SHIP] if doc_result else 0

    def process_total_seen_legendaries(self) -> dict:
        pipeline = [
            {"$match": {"cheater": False}},
            {"$project": {"leg_arti_list": {"$objectToArray": "$leg_arti_list"}}},
            {"$unwind": "$leg_arti_list"},
            {
                "$group": {
                    "_id": "$leg_arti_list.k",
                    "v": {"$sum": "$leg_arti_list.v"},
                }
            },
        ]

        logger.info("Starting query for total_seen_legendaries")
        docs_result = self.__get_coll__().aggregate(pipeline)
        result = {x["_id"]: x["v"] for x in docs_result}
        return result

    def process_legendaries_for_players(self) -> dict:
        pipeline = [
            {"$project": {"leg_arti_list": {"$objectToArray": "$leg_arti_list"}}},
            {
                "$project": {
                    "sum_leg_arti": {
                        "$sum": {
                            "$map": {
                                "input": "$leg_arti_list",
                                "as": "item",
                                "in": "$$item.v",
                            }
                        }
                    }
                }
            },
            {"$group": {"_id": "$sum_leg_arti", "v": {"$sum": 1}}},
        ]

        logger.info("Starting query for legendaries_for_players")
        docs_result = self.__get_coll__().aggregate(pipeline)
        result = OrderedDict({str(x["_id"]): x["v"] for x in docs_result})
        return result


class MongoReportCluster(BaseMongoManager):
    def __init__(self):
        super().__init__()
        self.connect(user_cluster=False)

    def __get_coll__(self):
        mydb = self.client["reports"]
        mycol = mydb["reports_collection"]
        return mycol

    def get_last_report(self):
        return next(self.__get_coll__().find().sort("date_insert", -1).limit(1), dict())
