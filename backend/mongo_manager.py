from collections import OrderedDict
from datetime import timedelta
import logging
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

        self.collection = self.client["players_db"]["players_collection"]

    def get_doc_from_eid(self, hashed_eid):
        return self.collection.find_one({"EID": hashed_eid})

    def upsert_user_doc(self, doc):
        logger.info(f"Upserting doc for hash {doc["EID"]}")
        self.collection.replace_one({"EID": doc["EID"]}, doc, upsert=True)

    def remove_old_users(self, days: int = 30):
        date_limit = utility.now_utc() - timedelta(days=days)
        result = self.collection.delete_many({"date_insert": {"$lt": date_limit}})
        print(f"Deleted {result.deleted_count} users")


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
        doc_result = next(self.collection.aggregate(pipeline), None)
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
        docs_result = self.collection.aggregate(pipeline)
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
        docs_result = self.collection.aggregate(pipeline)
        result = OrderedDict({str(x["_id"]): x["v"] for x in docs_result})
        return result


class MongoReportCluster(BaseMongoManager):
    def __init__(self):
        super().__init__()
        self.connect(user_cluster=False)

        self.collection = self.client["reports"]["reports_collection"]
        self.update_cached_results()

    def _clean_report(self, report: str | None):
        if not report:
            return report
        
        assert '_id' in report, "doc has no '_id'"
        report.pop('_id')
        return report


    def get_report_by_date_str(self, date_str: str):
        report = self.collection.find_one({"date_insert": date_str})
        return self._clean_report(report)

    def _update_latest_report(self):
       last_doc = next(self.collection.find().sort("date_insert", -1).limit(1), None)
       self.latest_report = self._clean_report(last_doc)

    def _update_report_dates(self):
        self.reports_timestamp = [el["date_insert"] for el in list(self.collection.find({},{"date_insert":1, "_id":0}).sort("date_insert", -1))]
    
    def update_cached_results(self):
        self._update_report_dates()
        self._update_latest_report()