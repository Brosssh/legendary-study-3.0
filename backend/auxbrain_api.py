import base64
import betterproto
import requests
import logging

from backend.errors import CorruptGameId
from backend.proto.ei import *

base_url = "https://ctx-dot-auxbrainhome.appspot.com/"
logger = logging.getLogger(__name__)
CURRENT_CLIENT_VERSION = 68


def _serialize(serializer: betterproto.Message):
    serialized_data = serializer.SerializeToString()
    encoded_data = base64.b64encode(serialized_data).decode("utf-8")
    return encoded_data

def _deserialize[T](encoded_data, deserializer: T, is_auth=False) -> T:
    decoded_data = base64.b64decode(encoded_data)
    if is_auth:
        auth = AuthenticatedMessage().parse(decoded_data)
        decoded_data = auth.message
    try:
        des = deserializer.parse(decoded_data)
    except UnicodeDecodeError as ex:
        raise UnicodeError(f"Could not parse this: {ex.object}. Kev put random non UTF-8 bytes in it. Set it to bytes if possible. Inner Expection: {ex}.")
    except Exception as e:
        logger.warning(f"Error in deserializer: {e})")
    else:
        return des

def get_player_data(EID) -> Backup:
    url = base_url + 'ei/bot_first_contact'
    serializer = EggIncFirstContactRequest()
    serializer.user_id = EID
    serializer.ei_user_id = EID
    serializer.client_version = CURRENT_CLIENT_VERSION
    serialized_request = _serialize(serializer)
    
    response = requests.post(url, data = { 'data' : serialized_request})

    if not response:
        raise CorruptGameId(EID)
    decoded_response = _deserialize(response.text, EggIncFirstContactResponse())
    if not decoded_response or decoded_response == "":
        raise CorruptGameId(EID)
    
    return decoded_response.backup