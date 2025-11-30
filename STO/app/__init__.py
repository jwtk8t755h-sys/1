from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    
    # Важно: добавь секретный ключ для работы форм
    app.config['SECRET_KEY'] = 'dev-secret-key-change-in-production'
    
    # Инициализируем расширения
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Регистрируем Blueprints
    from app.routes.main import main_bp
    from app.routes.admin import admin_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp)
    
    return app