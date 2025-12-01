from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import requests
from werkzeug.utils import secure_filename

# =============================================
# НАСТРОЙКА ПРИЛОЖЕНИЯ И БАЗЫ ДАННЫХ
# =============================================

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ваш-секретный-ключ-тут'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# =============================================
# НАСТРОЙКИ ЗАГРУЗКИ ФАЙЛОВ
# =============================================

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Создаем папку для загрузок если не существует
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_uploaded_file(file, lead_id, prefix):
    """Сохраняет загруженный файл и возвращает имя файла"""
    if file and file.filename and allowed_file(file.filename):
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')[:-3]
        filename = secure_filename(f"{prefix}_{lead_id}_{timestamp}.{file.filename.rsplit('.', 1)[1].lower()}")
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        return filename
    return None

# =============================================
# МОДЕЛИ БАЗЫ ДАННЫХ
# =============================================

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Financial(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(20), nullable=False)  # доход/расход
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50))
    lead_id = db.Column(db.Integer, db.ForeignKey('lead.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Lead(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(20), default='новая')
    
    # Поля для выполненных работ
    cost = db.Column(db.Float, nullable=True)
    work_description = db.Column(db.Text, nullable=True)
    photo_before = db.Column(db.String(200), nullable=True)
    photo_after = db.Column(db.String(200), nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Связь с финансовыми записями
    financial_records = db.relationship('Financial', backref='related_lead', lazy=True, foreign_keys='Financial.lead_id')

class TelegramSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bot_token = db.Column(db.String(200), nullable=True)
    chat_id = db.Column(db.String(100), nullable=True)
    is_active = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# =============================================
# ИНИЦИАЛИЗАЦИЯ БАЗЫ ДАННЫХ
# =============================================

with app.app_context():
    db.create_all()
    
    # Создаем тестового администратора если его нет
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin', password='admin123')
        db.session.add(admin)
        db.session.commit()
        print("✅ Создан тестовый администратор: admin / admin123")
    
    # Создаем настройки Telegram если их нет
    if not TelegramSettings.query.first():
        telegram_settings = TelegramSettings()
        db.session.add(telegram_settings)
        db.session.commit()
        print("✅ Созданы настройки Telegram")

# =============================================
# ФУНКЦИИ-ПОМОЩНИКИ
# =============================================

def send_telegram_notification(lead):
    settings = TelegramSettings.query.first()
    
    if not settings or not settings.is_active or not settings.bot_token or not settings.chat_id:
        return False
    
    try:
        message = f"""
🎯 *НОВАЯ ЗАЯВКА!*

*Имя:* {lead.name}
*Телефон:* `{lead.phone}`
*Адрес:* {lead.address}
*Дата:* {lead.created_at.strftime('%d.%m.%Y %H:%M')}

[Ссылка на заявку](http://localhost:5001/admin/leads)
        """
        
        url = f"https://api.telegram.org/bot{settings.bot_token}/sendMessage"
        data = {
            "chat_id": settings.chat_id,
            "text": message,
            "parse_mode": "Markdown",
            "disable_web_page_preview": True
        }
        
        response = requests.post(url, data=data, timeout=10)
        return response.status_code == 200
        
    except Exception as e:
        print(f"❌ Ошибка отправки в Telegram: {e}")
        return False

def update_financial_record(lead, cost):
    """Создает или обновляет финансовую запись для заявки"""
    if cost and cost > 0:
        # Ищем существующую финансовую запись для этой заявки
        existing_finance = Financial.query.filter_by(lead_id=lead.id).first()
        
        if existing_finance:
            # Обновляем существующую запись
            existing_finance.amount = cost
            existing_finance.description = f"Выполнение работ по заявке #{lead.id} - {lead.name}"
            existing_finance.created_at = datetime.utcnow()
        else:
            # Создаем новую запись
            financial_record = Financial(
                type='доход',
                amount=cost,
                description=f"Выполнение работ по заявке #{lead.id} - {lead.name}",
                category='выполненные работы',
                lead_id=lead.id,
                created_at=datetime.utcnow()
            )
            db.session.add(financial_record)
    else:
        # Если стоимость убрали, удаляем финансовую запись
        existing_finance = Financial.query.filter_by(lead_id=lead.id).first()
        if existing_finance:
            db.session.delete(existing_finance)

def calculate_monthly_financial_data():
    """Рассчитывает финансовые данные по месяцам за последний год"""
    from datetime import datetime, timedelta
    from collections import defaultdict
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    
    # Получаем финансовые операции за последний год
    financials = Financial.query.filter(
        Financial.created_at >= start_date
    ).all()
    
    # Группируем по месяцам
    monthly_income = defaultdict(float)
    monthly_expenses = defaultdict(float)
    
    for finance in financials:
        month_key = finance.created_at.strftime('%Y-%m')
        if finance.type == 'доход':
            monthly_income[month_key] += finance.amount
        else:
            monthly_expenses[month_key] += finance.amount
    
    # Сортируем месяцы
    months = sorted(monthly_income.keys())
    
    # Если данных нет, создаем демо-данные для отображения графиков
    if not months:
        current_month = datetime.now().strftime('%Y-%m')
        months = [current_month]
        monthly_income[current_month] = 0
        monthly_expenses[current_month] = 0
    
    return {
        'months': [datetime.strptime(month, '%Y-%m').strftime('%b') for month in months],
        'income': [monthly_income[month] for month in months],
        'expenses': [monthly_expenses[month] for month in months],
        'profit': [monthly_income[month] - monthly_expenses[month] for month in months]
    }

# =============================================
# КЛИЕНТСКИЕ МАРШРУТЫ (публичный сайт)
# =============================================

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit_form():
    name = request.form['name']
    phone = request.form['phone']
    address = request.form['address']
    
    new_lead = Lead(name=name, phone=phone, address=address)
    db.session.add(new_lead)
    db.session.commit()
    
    # Отправляем уведомление в Telegram
    send_telegram_notification(new_lead)
    
    print(f"🎯 НОВАЯ ЗАЯВКА: {name} - {phone} - {address}")
    
    return f'''
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Заявка принята!</title>
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                text-align: center;
                margin: 0;
                padding: 20px;
            }}
            .success-message {{
                background: rgba(255,255,255,0.1);
                padding: 40px;
                border-radius: 15px;
                backdrop-filter: blur(10px);
            }}
            .back-btn {{
                background: #28a745;
                color: white;
                border: none;
                padding: 15px 30px;
                border-radius: 50px;
                font-size: 1.1rem;
                cursor: pointer;
                margin-top: 20px;
                text-decoration: none;
                display: inline-block;
            }}
        </style>
    </head>
    <body>
        <div class="success-message">
            <h1>✅ Заявка принята!</h1>
            <p>Спасибо, {name}! Мы свяжемся с вами по телефону {phone} в течение 24 часов.</p>
            <p>Адрес объекта: {address}</p>
            <a href="/" class="back-btn">ВЕРНУТЬСЯ НА САЙТ</a>
        </div>
    </body>
    </html>
    '''

# =============================================
# АДМИН-МАРШРУТЫ (защищенная часть)
# =============================================

@app.route('/admin')
def admin_index():
    if 'admin_logged_in' not in session:
        return redirect(url_for('admin_login'))
    
    total_leads = Lead.query.count()
    new_leads = Lead.query.filter_by(status='новая').count()
    total_income = Financial.query.filter_by(type='доход').with_entities(db.func.sum(Financial.amount)).scalar() or 0
    total_expenses = Financial.query.filter_by(type='расход').with_entities(db.func.sum(Financial.amount)).scalar() or 0
    
    return render_template('admin/dashboard.html',
                         total_leads=total_leads,
                         new_leads=new_leads,
                         total_income=total_income,
                         total_expenses=total_expenses)

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username, password=password).first()
        
        if user:
            session['admin_logged_in'] = True
            session['admin_username'] = username
            flash('Успешный вход в админку!', 'success')
            return redirect(url_for('admin_index'))
        else:
            flash('Неверное имя пользователя или пароль', 'error')
    
    return render_template('admin/login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    session.pop('admin_username', None)
    flash('Вы вышли из системы', 'info')
    return redirect(url_for('admin_login'))

# =============================================
# УПРАВЛЕНИЕ ЗАЯВКАМИ (CRM)
# =============================================

@app.route('/admin/leads')
def admin_leads():
    if 'admin_logged_in' not in session:
        return redirect(url_for('admin_login'))
    
    leads = Lead.query.order_by(Lead.created_at.desc()).all()
    return render_template('admin/leads.html', leads=leads)

@app.route('/admin/lead/<int:lead_id>/update', methods=['POST'])
def update_lead_status(lead_id):
    if 'admin_logged_in' not in session:
        return redirect(url_for('admin_login'))
    
    lead = Lead.query.get_or_404(lead_id)
    lead.status = request.form['status']
    
    if lead.status == 'выполнена' and not lead.completed_at:
        lead.completed_at = datetime.utcnow()
    
    db.session.commit()
    flash('Статус заявки обновлен!', 'success')
    return redirect(url_for('admin_leads'))

@app.route('/admin/lead/<int:lead_id>/edit', methods=['GET', 'POST'])
def edit_lead(lead_id):
    if 'admin_logged_in' not in session:
        return redirect(url_for('admin_login'))
    
    lead = Lead.query.get_or_404(lead_id)
    
    if request.method == 'POST':
        lead.status = request.form['status']
        work_description = request.form['work_description']
        
        # Обработка стоимости
        old_cost = lead.cost
        new_cost = float(request.form['cost']) if request.form['cost'] else None
        lead.cost = new_cost
        
        # Обработка загруженных файлов
        if 'photo_before' in request.files:
            file = request.files['photo_before']
            filename = save_uploaded_file(file, lead_id, 'before')
            if filename:
                # Удаляем старый файл если есть
                if lead.photo_before:
                    old_file_path = os.path.join(app.config['UPLOAD_FOLDER'], lead.photo_before)
                    if os.path.exists(old_file_path):
                        os.remove(old_file_path)
                lead.photo_before = filename
        
        if 'photo_after' in request.files:
            file = request.files['photo_after']
            filename = save_uploaded_file(file, lead_id, 'after')
            if filename:
                # Удаляем старый файл если есть
                if lead.photo_after:
                    old_file_path = os.path.join(app.config['UPLOAD_FOLDER'], lead.photo_after)
                    if os.path.exists(old_file_path):
                        os.remove(old_file_path)
                lead.photo_after = filename
        
        lead.work_description = work_description
        
        # Если статус "выполнена", устанавливаем дату завершения
        if lead.status == 'выполнена' and not lead.completed_at:
            lead.completed_at = datetime.utcnow()
        
        # Обновляем финансовую запись при изменении стоимости
        if new_cost != old_cost:
            update_financial_record(lead, new_cost)
        
        db.session.commit()
        flash('Заявка обновлена!', 'success')
        return redirect(url_for('admin_leads'))
    
    return render_template('admin/edit_lead.html', lead=lead)

@app.route('/admin/lead/<int:lead_id>/delete', methods=['POST'])
def delete_lead(lead_id):
    if 'admin_logged_in' not in session:
        return redirect(url_for('admin_login'))
    
    lead = Lead.query.get_or_404(lead_id)
    
    # Удаляем связанные файлы
    if lead.photo_before:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], lead.photo_before)
        if os.path.exists(file_path):
            os.remove(file_path)
    
    if lead.photo_after:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], lead.photo_after)
        if os.path.exists(file_path):
            os.remove(file_path)
    
    # Удаляем финансовые записи связанные с этой заявкой
    financial_records = Financial.query.filter_by(lead_id=lead.id).all()
    for finance in financial_records:
        db.session.delete(finance)
    
    db.session.delete(lead)
    db.session.commit()
    
    flash('Заявка удалена!', 'success')
    return redirect(url_for('admin_leads'))

# =============================================
# ФИНАНСОВЫЙ УЧЕТ (ИСПРАВЛЕННАЯ ВЕРСИЯ)
# =============================================

@app.route('/admin/finances')
def admin_finances():
    if 'admin_logged_in' not in session:
        return redirect(url_for('admin_login'))
    
    # Получаем все финансовые операции
    finances = Financial.query.order_by(Financial.created_at.desc()).all()
    
    # ВЫЧИСЛЯЕМ ОСНОВНЫЕ СТАТИСТИКИ
    total_income = Financial.query.filter_by(type='доход').with_entities(db.func.sum(Financial.amount)).scalar() or 0
    total_expenses = Financial.query.filter_by(type='расход').with_entities(db.func.sum(Financial.amount)).scalar() or 0
    balance = total_income - total_expenses
    
    # Расчет данных для графиков
    income_by_category = {}
    expense_by_category = {}
    
    for finance in finances:
        if finance.type == 'доход':
            income_by_category[finance.category] = income_by_category.get(finance.category, 0) + finance.amount
        else:
            expense_by_category[finance.category] = expense_by_category.get(finance.category, 0) + finance.amount
    
    # Динамика по месяцам (последние 12 месяцев)
    monthly_data = calculate_monthly_financial_data()
    
    return render_template('admin/finances.html',
                         finances=finances,
                         total_income=total_income,
                         total_expenses=total_expenses,
                         balance=balance,
                         income_by_category=income_by_category,
                         expense_by_category=expense_by_category,
                         monthly_data=monthly_data)

@app.route('/add_financial', methods=['POST'])
def add_financial():
    if 'admin_logged_in' not in session:
        return redirect(url_for('admin_login'))
    
    try:
        financial = Financial(
            type=request.form['type'],
            amount=float(request.form['amount']),
            description=request.form['description'],
            category=request.form['category'],
            created_at=datetime.utcnow()
        )
        
        db.session.add(financial)
        db.session.commit()
        flash('Финансовая операция добавлена!', 'success')
        
    except Exception as e:
        flash(f'Ошибка при добавлении операции: {str(e)}', 'error')
    
    return redirect(url_for('admin_finances'))

@app.route('/delete_financial/<int:finance_id>', methods=['POST'])
def delete_financial(finance_id):
    if 'admin_logged_in' not in session:
        return redirect(url_for('admin_login'))
    
    financial = Financial.query.get_or_404(finance_id)
    db.session.delete(financial)
    db.session.commit()
    
    flash('Финансовая операция удалена!', 'success')
    return redirect(url_for('admin_finances'))

# =============================================
# НАСТРОЙКИ TELEGRAM И КАРТЫ
# =============================================

@app.route('/admin/telegram', methods=['GET', 'POST'])
def admin_telegram():
    if 'admin_logged_in' not in session:
        return redirect(url_for('admin_login'))
    
    settings = TelegramSettings.query.first()
    
    if request.method == 'POST':
        settings.bot_token = request.form['bot_token']
        settings.chat_id = request.form['chat_id']
        settings.is_active = 'is_active' in request.form
        settings.updated_at = datetime.utcnow()
        
        db.session.commit()
        flash('Настройки Telegram обновлены!', 'success')
        return redirect(url_for('admin_telegram'))
    
    return render_template('admin/telegram_settings.html', settings=settings)
@app.route('/admin/telegram_settings')
def telegram_settings():
    """Редирект для обратной совместимости со старыми шаблонами"""
    return redirect(url_for('admin_telegram'))
@app.route('/admin/map')
def admin_map():
    if 'admin_logged_in' not in session:
        return redirect(url_for('admin_login'))
    
    leads = Lead.query.all()
    return render_template('admin/map.html', leads=leads)

@app.route('/admin/telegram/test', methods=['POST'])
def test_telegram():
    if 'admin_logged_in' not in session:
        return {'success': False, 'error': 'Unauthorized'}, 401
    
    settings = TelegramSettings.query.first()
    if not settings or not settings.bot_token or not settings.chat_id:
        return {'success': False, 'error': 'Настройки не заполнены'}
    
    try:
        test_lead = Lead(
            name='Тестовый клиент',
            phone='+79990001122', 
            address='Тестовый адрес для проверки уведомлений',
            created_at=datetime.utcnow()
        )
        
        success = send_telegram_notification(test_lead)
        
        if success:
            return {'success': True}
        else:
            return {'success': False, 'error': 'Не удалось отправить сообщение'}
            
    except Exception as e:
        return {'success': False, 'error': str(e)}

# =============================================
# API ДЛЯ ПОЛУЧЕНИЯ ДАННЫХ В ФОРМАТЕ JSON
# =============================================

@app.route('/api/leads')
def api_leads():
    if 'admin_logged_in' not in session:
        return {'error': 'Unauthorized'}, 401
    
    leads = Lead.query.order_by(Lead.created_at.desc()).all()
    leads_data = []
    
    for lead in leads:
        lead_data = {
            'id': lead.id,
            'name': lead.name,
            'phone': lead.phone,
            'address': lead.address,
            'status': lead.status,
            'cost': lead.cost,
            'work_description': lead.work_description,
            'photo_before': lead.photo_before,
            'photo_after': lead.photo_after,
            'completed_at': lead.completed_at.isoformat() if lead.completed_at else None,
            'created_at': lead.created_at.isoformat()
        }
        leads_data.append(lead_data)
    
    return {'leads': leads_data}

@app.route('/api/finances')
def api_finances():
    if 'admin_logged_in' not in session:
        return {'error': 'Unauthorized'}, 401
    
    finances = Financial.query.order_by(Financial.created_at.desc()).all()
    finances_data = []
    
    for finance in finances:
        finance_data = {
            'id': finance.id,
            'type': finance.type,
            'amount': finance.amount,
            'description': finance.description,
            'category': finance.category,
            'lead_id': finance.lead_id,
            'created_at': finance.created_at.isoformat()
        }
        finances_data.append(finance_data)
    
    return {'finances': finances_data}

# =============================================
# ЗАПУСК ПРИЛОЖЕНИЯ
# =============================================

if __name__ == '__main__':
    app.run(debug=True, port=5001)