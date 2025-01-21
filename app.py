import logging
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from backend import mongo_manager
from backend.api_backend import submitEID
import backend.errors

load_dotenv()
logger = logging.getLogger()
logger.setLevel(logging.INFO)

mongo_instance = mongo_manager.mongo_manager()

app = Flask(__name__)

@app.errorhandler(Exception)
def handle_exception(e):
    if isinstance(e, backend.errors.CorruptGameId):
        logger.warning(f"EID {e} seems to be corrupted")
        return jsonify({'message': "EID corrupted"}), 412
    else:
        logger.error(e)
        return jsonify({'message': "Something went wrong, contact an administrator"}), 500
    
@app.route('/', methods=["GET"])
def main():
    pass

@app.route('/submitEID', methods=["POST"])
def submit():
    EID = request.form.get('EID')
    submitEID(EID)
    return {'message': "OK"}