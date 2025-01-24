import logging
from dotenv import load_dotenv
from flask import Flask, json, jsonify, request
from flasgger import Swagger
from backend import mongo_manager
from backend.api_backend import get_report, submitEID
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
    if isinstance(e, backend.errors.InvalidReportDate):
        return jsonify({'message': f"No report found for the given date {e}"}), 412
    if isinstance(e, backend.errors.InvalidDateFormat):
        return jsonify({'message': f"Date {e} is not valid. Date format should be 'YYYY-MM-DD' ('2024-12-30')"}), 412
    if isinstance(e, backend.errors.BadRequest):
        return jsonify({'message': f"Missing required parameter '{e}'. Check the API documentation at https://legendary-study-3-0.vercel.app/apidocs/"}), 400
    
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
        description: Invalid EID
      400:
        description: Missing EID
    """
    EID = request.form.get('EID', default=None)
    submitEID(EID)
    return {'message': "OK"}

@app.route('/getReportByDate', methods=["GET"])
def getReportByDate():
    """
    Get reports by a specific date. If 'date' is not specified, return the latest report.
    ---
    parameters:
      - name: date
        in: query
        type: string
        required: false
        description: The date in YYYY-MM-DD format. Empty if you want the latest report.
    responses:
      200:
        description: A list of reports for the given date.
      412:
        description: Invalid date format
    """
    date = request.args.get('date', default=None)
    response = json.jsonify(get_report(date))
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
