import datetime
import logging
from backend import mongo_manager
from backend.logger import init_logger

init_logger()
logger = logging.getLogger(__name__)

mongo_users = mongo_manager.MongoUserCluster()
mongo_reports = mongo_manager.MongoReportCluster()

logger.info("Removing old users...")
# mongo_users.remove_old_users()

logger.info("Starting new report process...")
old_report = mongo_reports.latest_report()

final_dict_report = {}
final_dict_report["date_insert"] = datetime.datetime.now().strftime('%Y-%m-%d')
final_dict_report["leg_seen"] = mongo_users.process_total_seen_legendaries()
final_dict_report["legendary_players"] = mongo_users.process_legendaries_for_players()
final_dict_report["zlc_record"] = max(mongo_users.process_zlc_record(), old_report["zlc_record"] if old_report else 0)
final_dict_report["number_total_users"]=mongo_users.collection.count_documents({})

logger.info("Loading new report to MongoDB...")
mongo_reports.collection.insert_one(final_dict_report)

logger.info("Updating timestamp and last cached doc")
mongo_reports.update_report_dates()
