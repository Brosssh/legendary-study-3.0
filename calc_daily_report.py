import datetime
import logging
from backend import mongo_manager
from backend import utility
from backend.utility import ZLC_SHIP

logger = logging.getLogger(__name__)

mongo_users = mongo_manager.MongoUserCluster()
mongo_reports = mongo_manager.MongoReportCluster()


# mongo_users.remove_old_users()
last_rep = mongo_reports.get_last_report()
last_rep["insert_date"] = datetime.datetime.now().strftime('%Y-%m-%d')
