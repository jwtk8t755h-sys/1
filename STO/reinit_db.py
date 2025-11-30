from app import create_app, db

def init_database():
    app = create_app()
    
    with app.app_context():
        # Создаем все таблицы
        db.create_all()
        print("✅ Все таблицы созданы успешно!")
        
        # Добавляем только основные данные без связей
        seed_basic_data()
        print("✅ Базовые данные добавлены!")

def seed_basic_data():
    # Добавляем марки автомобилей
    brands = [
        'Toyota', 'Honda', 'Ford', 'BMW', 'Mercedes-Benz',
        'Audi', 'Volkswagen', 'Nissan', 'Hyundai', 'Kia',
        'Chevrolet', 'Volvo', 'Mazda', 'Subaru', 'Lexus'
    ]
    
    for brand_name in brands:
        from app.models.vehicles import CarBrand
        brand = CarBrand(name=brand_name)
        db.session.add(brand)
    
    db.session.commit()
    print(f"✅ Добавлено {len(brands)} марок автомобилей")
    
    # Добавляем категории услуг
    categories = [
        'Диагностика',
        'Техническое обслуживание',
        'Ремонт двигателя',
        'Ремонт ходовой части',
        'Кузовные работы',
        'Электрика'
    ]
    
    for cat_name in categories:
        from app.models.services import ServiceCategory
        category = ServiceCategory(name=cat_name)
        db.session.add(category)
    
    db.session.commit()
    print(f"✅ Добавлено {len(categories)} категорий услуг")
    
    # Добавляем услуги
    services = [
        {'name': 'Компьютерная диагностика', 'price': 1500, 'category_id': 1},
        {'name': 'Замена масла', 'price': 2000, 'category_id': 2},
        {'name': 'Замена тормозных колодок', 'price': 3000, 'category_id': 2},
        {'name': 'Диагностика подвески', 'price': 1200, 'category_id': 4},
        {'name': 'Ремонт генератора', 'price': 5000, 'category_id': 6}
    ]
    
    for service_data in services:
        from app.models.services import ServiceType
        service = ServiceType(
            name=service_data['name'],
            base_price=service_data['price'],
            category_id=service_data['category_id']
        )
        db.session.add(service)
    
    db.session.commit()
    print(f"✅ Добавлено {len(services)} услуг")
    
    # Добавляем сотрудников
    employees = [
        {'first_name': 'Алексей', 'last_name': 'Иванов', 'position': 'Механик'},
        {'first_name': 'Дмитрий', 'last_name': 'Петров', 'position': 'Электрик'},
        {'first_name': 'Сергей', 'last_name': 'Сидоров', 'position': 'Мастер'}
    ]
    
    for emp_data in employees:
        from app.models.employees import Employee
        employee = Employee(
            first_name=emp_data['first_name'],
            last_name=emp_data['last_name'],
            position=emp_data['position']
        )
        db.session.add(employee)
    
    db.session.commit()
    print(f"✅ Добавлено {len(employees)} сотрудников")
    
    # Добавляем тестового клиента
    from app.models.clients import Client
    client = Client(
        first_name='Иван',
        last_name='Тестовый',
        phone='+79991234567',
        email='test@example.com'
    )
    db.session.add(client)
    db.session.commit()
    print("✅ Добавлен тестовый клиент")

if __name__ == '__main__':
    init_database()