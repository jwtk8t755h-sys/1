from app import db
from datetime import datetime

class CarBrand(db.Model):
    __tablename__ = 'car_brands'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    country = db.Column(db.String(20))  # european, asian, american
    is_active = db.Column(db.Boolean, default=True)
    
    models = db.relationship('CarModel', backref='brand', lazy=True)
    
    def __repr__(self):
        return f'<CarBrand {self.name}>'

class CarModel(db.Model):
    __tablename__ = 'car_models'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    brand_id = db.Column(db.Integer, db.ForeignKey('car_brands.id'), nullable=False)
    years = db.Column(db.String(100))  # диапазон годов выпуска
    is_active = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f'<CarModel {self.name}>'

class Vehicle(db.Model):
    __tablename__ = 'vehicles'
    
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    car_model_id = db.Column(db.Integer, db.ForeignKey('car_models.id'), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    vin = db.Column(db.String(17))
    license_plate = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Связи
    appointments = db.relationship('Appointment', backref='vehicle', lazy=True)
    
    def __repr__(self):
        return f'<Vehicle {self.license_plate or self.id}>'