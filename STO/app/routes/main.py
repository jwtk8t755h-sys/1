from flask import Blueprint, render_template, jsonify, request, flash, redirect, url_for
from datetime import datetime, date, timedelta
from app import db

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    try:
        from app.models.services import ServiceType
        from app.models.vehicles import CarBrand
        
        # Загружаем услуги и марки автомобилей
        services = ServiceType.query.filter_by(is_active=True).all()
        car_brands = CarBrand.query.filter_by(is_active=True).order_by(CarBrand.name).all()
        
        print(f"✅ Загружено услуг: {len(services)}")
        print(f"✅ Загружено марок автомобилей: {len(car_brands)}")
        
    except Exception as e:
        print(f"❌ Ошибка загрузки данных: {e}")
        services = []
        car_brands = []
    
    # Передаем сегодняшнюю дату для ограничения в календаре
    today = date.today().isoformat()
    return render_template('index.html', 
                         services=services, 
                         car_brands=car_brands,
                         today=today)

@main_bp.route('/create_appointment', methods=['POST'])
def create_appointment():
    try:
        # Получаем данные из формы
        name = request.form.get('name')
        phone = request.form.get('phone')
        car_brand_id = request.form.get('car_brand')
        car_model_name = request.form.get('car_model')
        car_year = request.form.get('car_year')
        service_id = request.form.get('service')
        date_str = request.form.get('date')
        time_str = request.form.get('time')
        notes = request.form.get('notes')
        
        # Проверяем обязательные поля
        if not all([name, phone, car_brand_id, car_model_name, car_year, service_id, date_str, time_str]):
            flash('Пожалуйста, заполните все обязательные поля', 'error')
            return redirect(url_for('main.index') + '#booking')
        
        # Проверяем дату
        appointment_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        if appointment_date < date.today():
            flash('Нельзя записаться на прошедшую дату', 'error')
            return redirect(url_for('main.index') + '#booking')
        
        # Проверяем день недели (0 - понедельник, 6 - воскресенье)
        if appointment_date.weekday() == 6:  # Воскресенье
            flash('Воскресенье - выходной день', 'error')
            return redirect(url_for('main.index') + '#booking')
        
        # Импортируем модели
        from app.models.clients import Client
        from app.models.vehicles import Vehicle, CarBrand, CarModel
        from app.models.appointments import Appointment
        from app.models.services import ServiceType
        
        # Создаем или находим клиента
        client = Client.query.filter_by(phone=phone).first()
        if not client:
            names = name.split()
            first_name = names[0] if names else ''
            last_name = ' '.join(names[1:]) if len(names) > 1 else ''
            
            client = Client(
                first_name=first_name,
                last_name=last_name,
                phone=phone,
                email=''
            )
            db.session.add(client)
            db.session.commit()
        
        # Обрабатываем марку автомобиля
        if car_brand_id == 'other':
            # Создаем временную марку "Другая"
            brand = CarBrand.query.filter_by(name='Другая').first()
            if not brand:
                brand = CarBrand(name='Другая', country='other')
                db.session.add(brand)
                db.session.commit()
        else:
            brand = CarBrand.query.get(car_brand_id)
        
        if not brand:
            flash('Ошибка выбора марки автомобиля', 'error')
            return redirect(url_for('main.index') + '#booking')
        
        # Создаем модель автомобиля
        car_model = CarModel.query.filter_by(name=car_model_name, brand_id=brand.id).first()
        if not car_model:
            car_model = CarModel(
                name=car_model_name,
                brand_id=brand.id,
                years=car_year
            )
            db.session.add(car_model)
            db.session.commit()
        
        # Создаем автомобиль
        vehicle = Vehicle(
            client_id=client.id,
            car_model_id=car_model.id,
            year=int(car_year),
            license_plate=f"TEMP_{phone[-4:]}"
        )
        db.session.add(vehicle)
        db.session.commit()
        
        # Получаем информацию об услуге
        service = ServiceType.query.get(service_id)
        if not service:
            flash('Выбранная услуга не найдена', 'error')
            return redirect(url_for('main.index') + '#booking')
        
        # Создаем запись
        appointment_datetime = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
        
        # Расчет времени окончания
        estimated_end_datetime = appointment_datetime + timedelta(minutes=service.standard_time_minutes)
        
        appointment = Appointment(
            client_id=client.id,
            vehicle_id=vehicle.id,
            service_id=int(service_id),
            employee_id=1,  # Временное значение
            appointment_datetime=appointment_datetime,
            estimated_end_datetime=estimated_end_datetime,
            notes=notes,
            status='scheduled'
        )
        db.session.add(appointment)
        db.session.commit()
        
        # Формируем сообщение об успехе
        success_message = (
            f'✅ Запись успешно создана!\n'
            f'📅 Дата: {appointment_datetime.strftime("%d.%m.%Y %H:%M")}\n'
            f'⏰ Расчетное время окончания: {estimated_end_datetime.strftime("%H:%M")}\n'
            f'🔧 Услуга: {service.name}\n'
            f'💰 Ориентировочная стоимость: от {service.base_price} руб.\n'
            f'📞 Мы свяжемся с вами для подтверждения.'
        )
        flash(success_message, 'success')
        return redirect(url_for('main.index') + '#booking')
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Ошибка создания записи: {e}")
        flash('❌ Произошла ошибка при создании записи. Пожалуйста, позвоните нам.', 'error')
        return redirect(url_for('main.index') + '#booking')
        # Проверяем обязательные поля
        if not all([name, phone, car_brand_id, car_model_name, service_id, date_str, time_str]):
            flash('Пожалуйста, заполните все обязательные поля', 'error')
            return redirect(url_for('main.index') + '#booking')
        
        # Проверяем дату (нельзя записаться на прошедшую дату)
        appointment_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        if appointment_date < date.today():
            flash('Нельзя записаться на прошедшую дату', 'error')
            return redirect(url_for('main.index') + '#booking')
        
        # Импортируем модели внутри функции чтобы избежать циклических импортов
        from app.models.clients import Client
        from app.models.vehicles import Vehicle, CarBrand, CarModel
        from app.models.appointments import Appointment
        from app.models.services import ServiceType
        
        # Создаем или находим клиента
        client = Client.query.filter_by(phone=phone).first()
        if not client:
            names = name.split()
            first_name = names[0] if names else ''
            last_name = ' '.join(names[1:]) if len(names) > 1 else ''
            
            client = Client(
                first_name=first_name,
                last_name=last_name,
                phone=phone,
                email=''
            )
            db.session.add(client)
            db.session.commit()
        
        # Находим марку автомобиля
        car_brand = CarBrand.query.get(car_brand_id)
        if not car_brand:
            flash('Выбранная марка автомобиля не найдена', 'error')
            return redirect(url_for('main.index') + '#booking')
        
        # Создаем модель автомобиля, если ее нет (упрощенно)
        car_model = CarModel.query.filter_by(name=car_model_name, brand_id=car_brand.id).first()
        if not car_model:
            car_model = CarModel(name=car_model_name, brand_id=car_brand.id)
            db.session.add(car_model)
            db.session.commit()
        
        # Создаем автомобиль
        vehicle = Vehicle(
            client_id=client.id,
            car_model_id=car_model.id,
            license_plate=f"TEMP_{phone[-4:]}"
        )
        db.session.add(vehicle)
        db.session.commit()
        
        # Получаем информацию об услуге для уведомления
        service = ServiceType.query.get(service_id)
        service_name = service.name if service else "Услуга"
        service_price = service.base_price if service else 0
        
        # Создаем запись
        appointment_datetime = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
        appointment = Appointment(
            client_id=client.id,
            vehicle_id=vehicle.id,
            service_id=int(service_id),
            employee_id=1,  # Временное значение - первый сотрудник
            appointment_datetime=appointment_datetime,
            notes=f"Марка: {car_brand.name}, Модель: {car_model_name}. {notes}",
            status='scheduled'
        )
        db.session.add(appointment)
        db.session.commit()
        
        # Формируем сообщение об успехе
        success_message = (
            f'✅ Запись успешно создана!\n'
            f'📅 Дата: {appointment_datetime.strftime("%d.%m.%Y %H:%M")}\n'
            f'🔧 Услуга: {service_name}\n'
            f'💰 Стоимость: от {service_price} руб.\n'
            f'📞 Мы свяжемся с вами для подтверждения.'
        )
        flash(success_message, 'success')
        return redirect(url_for('main.index') + '#booking')
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Ошибка создания записи: {e}")
        flash('❌ Произошла ошибка при создании записи. Пожалуйста, позвоните нам.', 'error')
        return redirect(url_for('main.index') + '#booking')

@main_bp.route('/api/status')
def api_status():
    status = {
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'version': '1.1'
    }
    return jsonify(status)