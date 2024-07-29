import os
import logging
from flask import Flask, request, jsonify, render_template, send_file, send_from_directory
from werkzeug.utils import secure_filename
from app.services.job_manager import JobManager
from app.services.document_handler import DocumentHandler
from app.services.query_manager import QueryManager
from app.services.data_extractor import DataExtractor
from app.services.output_generator import OutputGenerator
from app.services.llm_interface import LLMInterface

app = Flask(__name__, static_folder='../frontend/dist', template_folder='../frontend/dist')

logging.basicConfig(level=logging.DEBUG)
logging.getLogger('pdfminer').setLevel(logging.WARNING)

job_store = {}

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/begin_extraction', methods=['POST'])
def begin_extraction():
    job_manager = JobManager()
    job_manager.initialize_temp_dir()

    files = request.files.getlist('files')
    logging.info(f"Received {len(files)} files")
    for i, file in enumerate(files):
        filename = secure_filename(file.filename)
        path = os.path.join(job_manager.job_data["Temp Dir"], filename)
        file.save(path)
        alias = request.form.get(f'doc_alias_{i}')
        ext = request.form.get(f'doc_ext_{i}')
        logging.info(f"File {i}: filename={filename}, alias={alias}, ext={ext}")
        job_manager.job_data["Documents"].append({
            "Path": path,
            "Alias": alias,
            "Ext": ext
        })

    queries = []
    query_index = 0
    while f'query_text_{query_index}' in request.form:
        text = request.form.get(f'query_text_{query_index}')
        alias = request.form.get(f'query_alias_{query_index}')
        format = request.form.get(f'query_format_{query_index}')
        logging.info(f"Query {query_index}: text={text}, alias={alias}, format={format}")
        if text and alias and format:
            queries.append({
                "Text": text,
                "Alias": alias,
                "Format": format
            })
        query_index += 1
    job_manager.job_data["Queries"] = queries

    logging.info(f"Documents: {job_manager.job_data['Documents']}")
    logging.info(f"Queries: {job_manager.job_data['Queries']}")

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

    return jsonify(job_data)

@app.route('/download_results/<job_id>', methods=['GET'])
def download_results(job_id):
    logging.info(f"Download requested for job ID: {job_id}")

    job_manager = job_store.get(job_id)
    if not job_manager:
        logging.error(f"Job ID not found: {job_id}")
        return "Results file not found", 404

    job_data = job_manager.get_job_data()
    output_format = job_data["Export Format"]
    temp_dir = job_data["Temp Dir"]
    results_path = os.path.join(temp_dir, f'{job_id}.{output_format}')

    logging.info(f"Looking for results file at path: {results_path}")

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

if __name__ == "__main__":
    from app.cleanup import run_cleanup_job
    import threading
    cleanup_thread = threading.Thread(target=run_cleanup_job, daemon=True)
    cleanup_thread.start()
    app.run(debug=True)