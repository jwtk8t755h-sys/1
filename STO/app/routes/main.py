from flask import Blueprint, render_template, jsonify
from app.models.clients import Client
from app.models.appointments import Appointment
from app.models.services import ServiceType
from app import db
from datetime import datetime

# Создаем Blueprint
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    services = ServiceType.query.all()
    return render_template('index.html', services=services)

@main_bp.route('/api/status')
def api_status():
    status = {
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'version': '1.1'
    }
    return jsonify(status)