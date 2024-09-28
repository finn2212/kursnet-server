from flask import Flask
from flask_cors import CORS
from app.jobs.scheduler import schedule_jobs

def create_app():
    app = Flask(__name__)

    # Start the scheduler for all jobs
    schedule_jobs()
    
    # CORS settings
    CORS(app, resources={r"/*": {"origins": [
        "http://localhost:3000", 
        "https://dev-dela.xml-config-kursnet.de", 
        "https://dela.xml-config-kursnet.de"
    ]}}, supports_credentials=True)

    # Register Blueprints
    from app.routes.count_pages import count_pages_bp
    from app.routes.find_anbieter import find_anbieter_bp
    from app.routes.process_data import process_data_bp
    
    app.register_blueprint(count_pages_bp)
    app.register_blueprint(find_anbieter_bp)
    app.register_blueprint(process_data_bp)

    # Add more Blueprints as needed
    return app
