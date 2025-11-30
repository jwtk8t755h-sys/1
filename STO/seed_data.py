from app import create_app, db
from app.models.vehicles import CarBrand
from app.models.services import ServiceCategory, ServiceType
from app.models.employees import Employee
from app.models.clients import Client

def seed_initial_data():
    app = create_app()
    
    with app.app_context():
        print("🌱 Заполняем начальные данные...")
        
        # ТОЛЬКО ДОБАВЛЯЕМ ДАННЫЕ, НЕ УДАЛЯЕМ СТАРЫЕ
        
        # Проверяем, есть ли уже данные
        if CarBrand.query.count() > 0:
            print("⚠️  Данные уже существуют, пропускаем заполнение")
            return
        
        # Добавляем марки автомобилей (только если их нет)
        european_brands = [
            CarBrand(name='Volkswagen', country='Германия'),
            CarBrand(name='BMW', country='Германия'),
            CarBrand(name='Mercedes-Benz', country='Германия'),
            CarBrand(name='Audi', country='Германия'),
            CarBrand(name='Renault', country='Франция'),
            CarBrand(name='Peugeot', country='Франция'),
        ]
        
        asian_brands = [
            CarBrand(name='Toyota', country='Япония'),
            CarBrand(name='Honda', country='Япония'),
            CarBrand(name='Nissan', country='Япония'),
            CarBrand(name='Hyundai', country='Корея'),
            CarBrand(name='Kia', country='Корея'),
            CarBrand(name='Mitsubishi', country='Япония'),
        ]
        
        american_brands = [
            CarBrand(name='Ford', country='США'),
            CarBrand(name='Chevrolet', country='США'),
            CarBrand(name='Chrysler', country='США'),
        ]
        
        all_brands = european_brands + asian_brands + american_brands
        
        for brand in all_brands:
            db.session.add(brand)
        
        db.session.commit()
        print("✅ Марки автомобилей добавлены")
        
        # Продолжаем с остальными данными...
        # ... (остальной код без изменений)
        
        # Добавляем категории услуг
        categories = [
            ServiceCategory(name='Диагностика', description='Комплексная диагностика автомобиля'),
            ServiceCategory(name='Техническое обслуживание', description='Плановое ТО и замена жидкостей'),
            ServiceCategory(name='Ремонт двигателя', description='Ремонт и обслуживание ДВС'),
            ServiceCategory(name='Тормозная система', description='Ремонт и замена тормозов'),
            ServiceCategory(name='Ходовая часть', description='Подвеска и рулевое управление'),
            ServiceCategory(name='Электрика', description='Электрооборудование и проводка'),
            ServiceCategory(name='Кондиционеры', description='Обслуживание и ремонт климат-систем'),
        ]
        
        for category in categories:
            db.session.add(category)
        
        db.session.commit()
        print("✅ Категории услуг добавлены")
        
        # Ждем пока категории сохранятся в БД
        categories_from_db = ServiceCategory.query.all()
        categories_dict = {cat.name: cat.id for cat in categories_from_db}
        
        # Добавляем типы услуг
        service_types = [
            ServiceType(
                category_id=categories_dict['Диагностика'],
                name='Компьютерная диагностика',
                description='Сканирование ошибок электронных систем',
                standard_time_hours=0.5,
                base_price=1500
            ),
            ServiceType(
                category_id=categories_dict['Диагностика'],
                name='Диагностика ходовой части',
                description='Проверка состояния подвески',
                standard_time_hours=0.5,
                base_price=1000
            ),
            ServiceType(
                category_id=categories_dict['Техническое обслуживание'],
                name='Замена масла двигателя',
                description='Замена моторного масла и масляного фильтра',
                standard_time_hours=0.5,
                base_price=2000
            ),
            ServiceType(
                category_id=categories_dict['Техническое обслуживание'],
                name='Замена воздушного фильтра',
                description='Замена фильтра воздушной системы',
                standard_time_hours=0.2,
                base_price=500
            ),
            ServiceType(
                category_id=categories_dict['Тормозная система'],
                name='Замена тормозных колодок',
                description='Замена передних или задних тормозных колодок',
                standard_time_hours=1.0,
                base_price=2500
            ),
        ]
        
        for service_type in service_types:
            db.session.add(service_type)
        
        db.session.commit()
        print("✅ Типы услуг добавлены")
        
        # Добавляем сотрудников
        employees = [
            Employee(name='Иванов Алексей', phone='+79161234567', specialty='Мастер-приемщик'),
            Employee(name='Петров Дмитрий', phone='+79161234568', specialty='Автослесарь'),
            Employee(name='Сидоров Михаил', phone='+79161234569', specialty='Электрик'),
        ]
        
        for employee in employees:
            db.session.add(employee)
        
        db.session.commit()
        print("✅ Сотрудники добавлены")
        
        # Добавляем тестового клиента
        test_client = Client(
            name='Петров Иван',
            phone='+79160000001',
            email='petrov@example.com'
        )
        db.session.add(test_client)
        db.session.commit()
        print("✅ Тестовый клиент добавлен")
        
        print("🎉 Начальные данные успешно заполнены!")
        print(f"📊 Добавлено:")
        print(f"   - {len(all_brands)} марок автомобилей")
        print(f"   - {len(categories)} категорий услуг")
        print(f"   - {len(service_types)} типов услуг")
        print(f"   - {len(employees)} сотрудников")
        print(f"   - 1 тестовый клиент")

if __name__ == '__main__':
    seed_initial_data()