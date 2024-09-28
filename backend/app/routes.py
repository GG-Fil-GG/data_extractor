import os
import logging
from flask import request, jsonify, send_file, send_from_directory, url_for
from werkzeug.utils import secure_filename
from app.services.job_manager import JobManager
from app.services.document_handler import DocumentHandler
from app.services.query_manager import QueryManager
from app.services.data_extractor import DataExtractor
from app.services.output_generator import OutputGenerator
from app.services.llm_interface import LLMInterface
from flask import Blueprint, jsonify
import json

main = Blueprint('main', __name__)

logging.basicConfig(level=logging.DEBUG)
logging.getLogger('pdfminer').setLevel(logging.WARNING)

job_store = {}

@main.route('/begin_extraction', methods=['POST'])
def begin_extraction():
    logging.info("Received request for begin_extraction")
    logging.info(f"Request method: {request.method}")
    logging.info(f"Request headers: {request.headers}")
    logging.info(f"Request form data: {request.form}")
    logging.info(f"Request files: {request.files}")
    
    try:
        job_manager = JobManager()
        job_manager.initialize_temp_dir()

        documents_data = json.loads(request.form['documents'])
        processed_documents = []

        for index, doc_metadata in enumerate(documents_data):
            file_key = f'file_{index}'
            if file_key in request.files:
                file = request.files[file_key]
                filename = secure_filename(file.filename)
                path = os.path.join(job_manager.job_data["Temp Dir"], filename)
                file.save(path)
                
                if 'Alias' not in doc_metadata or 'Ext' not in doc_metadata:
                    logging.error(f"Missing Alias or Ext for document at index {index}")
                    continue

                processed_doc = {
                    "Path": path,
                    "Alias": doc_metadata['Alias'],
                    "Ext": doc_metadata['Ext']
                }
                processed_documents.append(processed_doc)
                logging.info(f"Processed document: {processed_doc}")
            else:
                logging.warning(f"File not found for document at index {index}")

        job_manager.job_data["Documents"] = processed_documents

        # Parse queries
        job_manager.job_data["Queries"] = json.loads(request.form['queries'])

        # Parse export format and orientation
        job_manager.job_data["Export Format"] = request.form['export_format']
        job_manager.job_data["Orientation"] = request.form['orientation']

        document_handler = DocumentHandler(job_manager)
        query_manager = QueryManager(job_manager)

        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY not set in .env file")
        llm_interface = LLMInterface(api_key)

        data_extractor = DataExtractor(job_manager, document_handler, query_manager, llm_interface)
        job_data = data_extractor.run()

        output_generator = OutputGenerator(job_manager)
        output_generator.generate_output()

        job_store[job_manager.job_data["Job ID"]] = job_manager

        return jsonify({"job_id": job_manager.job_data["Job ID"]})
    except Exception as e:
        logging.error(f"Error in begin_extraction: {str(e)}")
        return jsonify({"error": str(e)}), 500

@main.route('/download_results', methods=['GET'])
def download_results():
    job_id = request.args.get('job_id')
    if not job_id:
        return jsonify({"error": "No job ID provided"}), 400

    job_manager = job_store.get(job_id)
    if not job_manager:
        logging.error(f"Job ID not found: {job_id}")
        return jsonify({"error": "Results file not found"}), 404

    job_data = job_manager.get_job_data()
    output_format = job_data["Export Format"]
    
    # Generate a URL for the actual file download
    download_url = url_for('main.get_file', job_id=job_id, _external=True)
    
    return jsonify({"downloadUrl": download_url})

@main.route('/get_file/<job_id>', methods=['GET'])
def get_file(job_id):
    job_manager = job_store.get(job_id)
    if not job_manager:
        logging.error(f"Job ID not found: {job_id}")
        return "Results file not found", 404

    job_data = job_manager.get_job_data()
    output_format = job_data["Export Format"]
    temp_dir = job_data["Temp Dir"]
    results_path = os.path.join(temp_dir, f'{job_id}.{output_format}')

    if not os.path.exists(results_path):
        logging.error(f"Results file not found at path: {results_path}")
        return "Results file not found", 404

    response = send_file(results_path, as_attachment=True, download_name=f'{job_id}.{output_format}')

    def cleanup_temp_dir():
        logging.info(f"Cleaning up temporary directory: {temp_dir}")
        try:
            job_manager.finalize_extraction()
            logging.info(f"Temporary directory {temp_dir} deleted successfully.")
        except Exception as e:
            logging.error(f"Error while cleaning up temporary directory: {e}")
        finally:
            if job_id in job_store:
                del job_store[job_id]
                logging.info(f"Job {job_id} removed from job_store.")

    response.call_on_close(cleanup_temp_dir)

    return response

@main.route('/test', methods=['GET'])
def test():
    print("Test route accessed")  # Add this line
    return jsonify({"message": "Test successful"}), 200

print("Routes registered")  # Add this line