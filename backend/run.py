from app import create_app
from app.cleanup import run_cleanup_job
import threading

app = create_app()

if __name__ == "__main__":
    cleanup_thread = threading.Thread(target=run_cleanup_job, daemon=True)
    cleanup_thread.start()
    app.run(host='0.0.0.0', port=5001, debug=True)