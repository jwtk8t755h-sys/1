from app import create_app, db
from app.models.vehicles import CarBrand, CarModel
from app.models.services import ServiceCategory, ServiceType
from app.models.employees import Employee
import json

def populate_database():
    app = create_app()
    
    with app.app_context():
        print("🗃️ Наполняем базу данных...")
        
        # Добавляем марки автомобилей
        car_brands_data = [
            # Европейские марки
            {'name': 'Volkswagen', 'country': 'european'},
            {'name': 'BMW', 'country': 'european'},
            {'name': 'Mercedes-Benz', 'country': 'european'},
            {'name': 'Audi', 'country': 'european'},
            {'name': 'Renault', 'country': 'european'},
            {'name': 'Peugeot', 'country': 'european'},
            {'name': 'Opel', 'country': 'european'},
            {'name': 'Skoda', 'country': 'european'},
            {'name': 'Volvo', 'country': 'european'},
            
            # Азиатские марки
            {'name': 'Toyota', 'country': 'asian'},
            {'name': 'Honda', 'country': 'asian'},
            {'name': 'Nissan', 'country': 'asian'},
            {'name': 'Hyundai', 'country': 'asian'},
            {'name': 'Kia', 'country': 'asian'},
            {'name': 'Mitsubishi', 'country': 'asian'},
            {'name': 'Mazda', 'country': 'asian'},
            {'name': 'Subaru', 'country': 'asian'},
            {'name': 'Lexus', 'country': 'asian'},
            
            # Американские марки
            {'name': 'Ford', 'country': 'american'},
            {'name': 'Chevrolet', 'country': 'american'},
            {'name': 'Chrysler', 'country': 'american'},
            {'name': 'Jeep', 'country': 'american'},
            {'name': 'Dodge', 'country': 'american'},
        ]
        
        for brand_data in car_brands_data:
            brand = CarBrand.query.filter_by(name=brand_data['name']).first()
            if not brand:
                brand = CarBrand(
                    name=brand_data['name'],
                    country=brand_data['country']
                )
                db.session.add(brand)
        
        db.session.commit()
        print(f"✅ Добавлено {len(car_brands_data)} марок автомобилей")
        
        # Добавляем популярные модели
        car_models_data = [
            # Volkswagen
            {'name': 'Golf', 'brand_name': 'Volkswagen', 'years': '1974-2024'},
            {'name': 'Passat', 'brand_name': 'Volkswagen', 'years': '1973-2024'},
            {'name': 'Tiguan', 'brand_name': 'Volkswagen', 'years': '2007-2024'},
            
            # Toyota
            {'name': 'Camry', 'brand_name': 'Toyota', 'years': '1982-2024'},
            {'name': 'Corolla', 'brand_name': 'Toyota', 'years': '1966-2024'},
            {'name': 'RAV4', 'brand_name': 'Toyota', 'years': '1994-2024'},
            
            # BMW
            {'name': '3 Series', 'brand_name': 'BMW', 'years': '1975-2024'},
            {'name': '5 Series', 'brand_name': 'BMW', 'years': '1972-2024'},
            {'name': 'X5', 'brand_name': 'BMW', 'years': '1999-2024'},
            
            # Ford
            {'name': 'Focus', 'brand_name': 'Ford', 'years': '1998-2024'},
            {'name': 'Mondeo', 'brand_name': 'Ford', 'years': '1993-2024'},
            {'name': 'Kuga', 'brand_name': 'Ford', 'years': '2008-2024'},
        ]
        
        for model_data in car_models_data:
            brand = CarBrand.query.filter_by(name=model_data['brand_name']).first()
            if brand:
                model = CarModel.query.filter_by(name=model_data['name'], brand_id=brand.id).first()
                if not model:
                    model = CarModel(
                        name=model_data['name'],
                        brand_id=brand.id,
                        years=model_data['years']
                    )
                    db.session.add(model)
        
        db.session.commit()
        print(f"✅ Добавлено популярных моделей автомобилей")
        
        # Добавляем категории услуг
        categories = [
            {'name': 'Диагностика', 'description': 'Компьютерная и механическая диагностика'},
            {'name': 'Техническое обслуживание', 'description': 'Регулярное ТО и плановое обслуживание'},
            {'name': 'Ремонт двигателя', 'description': 'Ремонт и обслуживание двигателей'},
            {'name': 'Трансмиссия', 'description': 'Ремонт КПП, сцепления, приводов'},
            {'name': 'Ходовая часть', 'description': 'Подвеска, рулевое управление'},
            {'name': 'Тормозная система', 'description': 'Тормозные колодки, диски, жидкости'},
            {'name': 'Электрика', 'description': 'Электрооборудование, проводка'},
            {'name': 'Кондиционеры', 'description': 'Обслуживание и ремонт климат-систем'},
        ]
        
        for cat_data in categories:
            category = ServiceCategory.query.filter_by(name=cat_data['name']).first()
            if not category:
                category = ServiceCategory(
                    name=cat_data['name'],
                    description=cat_data['description']
                )
                db.session.add(category)
        
        db.session.commit()
        print(f"✅ Добавлено {len(categories)} категорий услуг")
        
        # Добавляем услуги с нормативами времени (в минутах)
        services_data = [
            # Диагностика
            {'name': 'Компьютерная диагностика', 'price': 1500, 'time': 30, 'category': 'Диагностика'},
            {'name': 'Диагностика подвески', 'price': 1200, 'time': 45, 'category': 'Диагностика'},
            {'name': 'Диагностика двигателя', 'price': 2000, 'time': 60, 'category': 'Диагностика'},
            
            # ТО
            {'name': 'Замена масла двигателя', 'price': 2000, 'time': 30, 'category': 'Техническое обслуживание'},
            {'name': 'Замена воздушного фильтра', 'price': 500, 'time': 15, 'category': 'Техническое обслуживание'},
            {'name': 'Замена салонного фильтра', 'price': 600, 'time': 20, 'category': 'Техническое обслуживание'},
            
            # Ремонт двигателя
            {'name': 'Замена ремня ГРМ', 'price': 8000, 'time': 240, 'category': 'Ремонт двигателя'},
            {'name': 'Замена цепи ГРМ', 'price': 12000, 'time': 360, 'category': 'Ремонт двигателя'},
            {'name': 'Замена свечей зажигания', 'price': 1500, 'time': 45, 'category': 'Ремонт двигателя'},
            
            # Тормозная система
            {'name': 'Замена тормозных колодок', 'price': 3000, 'time': 90, 'category': 'Тормозная система'},
            {'name': 'Замена тормозных дисков', 'price': 5000, 'time': 120, 'category': 'Тормозная система'},
            {'name': 'Замена тормозной жидкости', 'price': 1500, 'time': 60, 'category': 'Тормозная система'},
            
            # Ходовая часть
            {'name': 'Замена амортизаторов', 'price': 6000, 'time': 180, 'category': 'Ходовая часть'},
            {'name': 'Замена шаровых опор', 'price': 4000, 'time': 120, 'category': 'Ходовая часть'},
            {'name': 'Замена сайлентблоков', 'price': 4500, 'time': 150, 'category': 'Ходовая часть'},
            
            # Электрика
            {'name': 'Замена аккумулятора', 'price': 1000, 'time': 20, 'category': 'Электрика'},
            {'name': 'Замена генератора', 'price': 5000, 'time': 120, 'category': 'Электрика'},
            {'name': 'Замена стартера', 'price': 4500, 'time': 90, 'category': 'Электрика'},
            
            # Кондиционеры
            {'name': 'Заправка кондиционера', 'price': 2500, 'time': 60, 'category': 'Кондиционеры'},
            {'name': 'Замена компрессора', 'price': 8000, 'time': 180, 'category': 'Кондиционеры'},
        ]
        
        for service_data in services_data:
            category = ServiceCategory.query.filter_by(name=service_data['category']).first()
            if category:
                service = ServiceType.query.filter_by(name=service_data['name']).first()
                if not service:
                    service = ServiceType(
                        name=service_data['name'],
                        base_price=service_data['price'],
                        standard_time_minutes=service_data['time'],
                        category_id=category.id
                    )
                    db.session.add(service)
        
        db.session.commit()
        print(f"✅ Добавлено {len(services_data)} услуг с нормативами времени")
        
        # Добавляем сотрудников
        employees = [
            {'first_name': 'Алексей', 'last_name': 'Иванов', 'position': 'Старший механик'},
            {'first_name': 'Дмитрий', 'last_name': 'Петров', 'position': 'Механик'},
            {'first_name': 'Сергей', 'last_name': 'Сидоров', 'position': 'Электрик'},
            {'first_name': 'Михаил', 'last_name': 'Козлов', 'position': 'Мастер приемщик'},
        ]
        
        for emp_data in employees:
            employee = Employee.query.filter_by(first_name=emp_data['first_name'], last_name=emp_data['last_name']).first()
            if not employee:
                employee = Employee(
                    first_name=emp_data['first_name'],
                    last_name=emp_data['last_name'],
                    position=emp_data['position']
                )
                db.session.add(employee)
        
        db.session.commit()
        print(f"✅ Добавлено {len(employees)} сотрудников")
        
        print("🎉 База данных наполнена успешно!")

if __name__ == '__main__':
    populate_database()