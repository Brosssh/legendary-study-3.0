import logging
from dotenv import load_dotenv
from flask import Flask, json, jsonify, request
from flasgger import Swagger
from backend import mongo_manager
from backend.api_backend import submitEID
import backend.errors
from backend.logger import init_logger

load_dotenv()

init_logger()

# Initialize clusters
_ = mongo_manager.MongoUserCluster()
mongo_reports = mongo_manager.MongoReportCluster()

template = {
  "swagger": "2.0",
  "info": {
    "title": "Legendary Study API",
    "description": "The backend that collect and prepare daily reports for the Wasmegg Legendary Study",
    "contact": {
      "responsibleDeveloper": "Brosssh",
    },
    "version": "0.0.1"
  }
}

app = Flask(__name__)
swagger = Swagger(app, template=template)

logger = logging.getLogger(__name__)

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
    """
    Home
    ---
    responses:
      200:
        description: Home page information
    """
    return "If you are wondering how to use this, check https://github.com/Brosssh/legendary-study-3.0"

@app.route('/submitEID', methods=["POST"])
def submit():
    """
    Submit an EID
    ---
    parameters:
      - name: EID
        in: formData
        type: string
        required: true
        description: The EID to be submitted.
    responses:
      200:
        description: EID submitted successfully
      412:
        description: Invalid or missing EID
    """
    EID = request.form.get('EID')
    submitEID(EID)
    return {'message': "OK"}

@app.route('/getReportByDate', methods=["GET"])
def getReportByDate():
    """
    Get reports by a specific date
    ---
    parameters:
      - name: date
        in: query
        type: string
        required: true
        description: The date in YYYY-MM-DD format.
    responses:
      200:
        description: A list of reports for the given date.
      412:
        description: Invalid date format
    """
    date = request.args.get('date') #TODO date check
    response = json.jsonify(mongo_reports.get_report_by_date_str(date))
    return response

@app.route('/getLatestReport', methods=["GET"])
def getLatestReport():
    """
    Get the latest report
    ---
    responses:
      200:
        description: The latest loaded report.
    """
    response = json.jsonify(mongo_reports.latest_report)
    return response

@app.route('/getTimestampsReport', methods=["GET"])
def getTimestampsReport():
    """
    Get the list of past dates that have a report
    ---
    responses:
      200:
        description: Get the list of past dates that have a report.
    """
    response = json.jsonify(mongo_reports.reports_timestamp)
    return response

if __name__ == '__main__':
    app.run(debug=True)
