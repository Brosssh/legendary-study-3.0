import datetime
import logging
from backend import mongo_manager, utility
from backend.logger import init_logger

init_logger()
logger = logging.getLogger(__name__)

mongo_users = mongo_manager.MongoUserCluster()
mongo_reports = mongo_manager.MongoReportCluster()

logger.info("Removing old users...")
mongo_users.remove_old_users()

logger.info("Starting new report process...")

today_date_str = datetime.datetime.now().strftime('%Y-%m-%d')
 
if mongo_reports.latest_report and mongo_reports.latest_report["date_insert"] == today_date_str: #Doc already exists, should never happen unless manual run
    logger.warning(f"Doc for today ({today_date_str}) already exist. Recalculating and updating...")
    #Taking doc of yesterday as last valid doc
    yesterday_date_str = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    last_valid_report = mongo_reports.get_report_by_date_str(yesterday_date_str)
else:
    last_valid_report = mongo_reports.latest_report

final_dict_report = {}
final_dict_report["date_insert"] = today_date_str
final_dict_report["leg_seen"] = mongo_users.process_total_seen_legendaries()
final_dict_report["legendary_players"] = mongo_users.process_legendaries_for_players()
final_dict_report["number_total_users"]=mongo_users.collection.count_documents({})

if ((new_zlc_record := mongo_users.process_zlc_record()) > last_valid_report["zlc_record"]["amount"] if last_valid_report else -1): #If no reports, new ZLC by default
    #New ZLC record
    final_dict_report["zlc_record"] = {
        "amount": new_zlc_record,
        "registered_on": utility.now_utc().strftime('%Y-%m-%d')
    }
else:
    final_dict_report["zlc_record"] = last_valid_report["zlc_record"]

logger.info("Loading new report to MongoDB...")
mongo_reports.collection.update_one({"date_insert": final_dict_report["date_insert"]}, {"$set": final_dict_report}, upsert=True) #Update just in case i want to recalcuate it for some reason

logger.info("Updating report date lists and last cached doc")
mongo_reports.update_cached_results()

logger.info(f"Run succedeed. Loaded report for date {final_dict_report["date_insert"]}")
