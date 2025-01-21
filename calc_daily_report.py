import datetime
import logging
from backend import mongo_manager
from backend.utility import ZLC_SHIP

logger = logging.getLogger(__name__)

mongo_users = mongo_manager.MongoUserCluster()
mongo_reports = mongo_manager.MongoReportCluster()


def zlc_record() -> int:
    pipeline = [
        {
            "$match": {
                "cheater": False,
                f"ships_count.{ZLC_SHIP}": {"$exists": True, "$gt": 0},
                "leg_arti_list": {"$size": 0},
            }
        },
        {"$sort": {f"ships_count.{ZLC_SHIP}": -1}},
        {"$limit": 1},
    ]
    logger.info("Starting query for zlc_record")
    doc_result = next(mongo_users.__get_coll__().aggregate(pipeline), None)
    return doc_result["ships_count"][ZLC_SHIP] if doc_result else 0


def total_seen_legendaries() -> dict:
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
        {"$sort": {"v": -1}},
    ]

    logger.info("Starting query for total_seen_legendaries")
    docs_result = mongo_users.__get_coll__().aggregate(pipeline)
    result = {x["_id"]: x["v"] for x in docs_result}
    return result


def legendaries_for_players() -> dict:
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
        {"$sort": {"_id": -1}},
    ]

    logger.info("Starting query for legendaries_for_players")
    docs_result = mongo_users.__get_coll__().aggregate(pipeline)
    result = {x["_id"]: x["v"] for x in docs_result}
    return result


# mongo_users.remove_old_users()

i = legendaries_for_players()
fddf = 2
