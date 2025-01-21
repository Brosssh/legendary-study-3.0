from collections import Counter
from datetime import timezone, timedelta
import logging
import re
from collections import Counter
from backend import auxbrain_api
from backend import utility
from backend.errors import CorruptGameId
from backend.proto.ei import ArtifactSpecRarity
from backend.utility import hash_str
from backend import mongo_manager

logger = logging.getLogger(__name__)

def submitEID(EID):
    if not re.match(r"^EI\d{16}$", EID):
        return
    
    hashed_eid = hash_str(EID)
    
    mongo_instance = mongo_manager.mongo_manager()
    user = mongo_instance.get_doc_from_eid(hashed_eid)
    if user and user["cheater"]:
        logger.info(f"Skipping hash {hashed_eid} since cheater")
    
    if user and (user["date_insert"].replace(tzinfo=timezone.utc) + timedelta(hours=1)) > utility.now_utc():
        logger.info(f"Not updating hash {hashed_eid} since backup is recent")

    backup = auxbrain_api.get_player_data(EID)

    doc = {"EID": hashed_eid}
    
    ships_count = Counter(f"{el.ship}:{el.duration_type}" for el in backup.artifacts_db.mission_archive)
    doc["ships_count"] = dict(ships_count) 

    leg_arti_list = [x for x in backup.artifacts_db.inventory_items if x.artifact.spec.rarity == ArtifactSpecRarity.LEGENDARY]
    leg_arti_count = Counter(f"{el.artifact.spec.name}:{el.artifact.spec.level}" for el in leg_arti_list)
    doc["leg_arti_list"] = dict(leg_arti_count)

    any_no_id_leg = any(1 for x in leg_arti_list if not x.server_id)
    doc["any_no_id_leg"] = any_no_id_leg

    any_duped_leg = any(x for x in leg_arti_list if x.quantity > 1)
    doc["any_duped_leg"] = any_duped_leg

    ship_ids = [i.identifier for i in backup.artifacts_db.mission_archive]
    any_ship_duped = len(set(ship_ids)) != len(ship_ids)
    doc["any_ship_duped"] = any_ship_duped

    doc["cheater"] = any_no_id_leg or any_duped_leg or any_ship_duped

    doc["date_insert"] = utility.now_utc() 

    mongo_instance.upsert_user_doc(doc)