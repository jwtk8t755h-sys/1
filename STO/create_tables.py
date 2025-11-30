from app import create_app, db
from app.models.clients import Client
from app.models.vehicles import CarBrand, CarModel, Vehicle
from app.models.services import ServiceCategory, ServiceType
from app.models.employees import Employee
from app.models.appointments import Appointment

def create_tables():
    app = create_app()
    
    with app.app_context():
        try:
            # Создаем все таблицы
            db.create_all()
            print("✅ Все таблицы созданы успешно!")
            
            # Добавляем минимальные тестовые данные
            add_test_data()
            print("✅ Тестовые данные добавлены!")
            
        except Exception as e:
            print(f"❌ Ошибка: {e}")

def add_test_data():
    # Добавляем только самые основные данные без сложных связей
    brand = CarBrand(name="Toyota")
    db.session.add(brand)
    
    category = ServiceCategory(name="Диагностика")
    db.session.add(category)
    
    service = ServiceType(name="Компьютерная диагностика", base_price=1500, category_id=1)
    db.session.add(service)
    
    employee = Employee(first_name="Иван", last_name="Тестовый", position="Механик")
    db.session.add(employee)
    
    client = Client(first_name="Тест", last_name="Клиент", phone="+79991234567")
    db.session.add(client)
    
    db.session.commit()

if __name__ == '__main__':
    create_tables()