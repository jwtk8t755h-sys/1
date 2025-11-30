from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app.models.clients import Client
from app import db

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/')
def dashboard():
    print("🔍 Доступ к дашборду...")
    try:
        total_clients = Client.query.count()
        print(f"✅ Клиентов: {total_clients}")
    except Exception as e:
        print(f"❌ Ошибка при подсчете клиентов: {e}")
        total_clients = 0
    
    return render_template('admin/dashboard.html',
                         total_clients=total_clients,
                         total_appointments=0,
                         today_appointments=0)

@admin_bp.route('/clients')
def clients_list():
    print("🔍 Доступ к списку клиентов...")
    try:
        clients = Client.query.all()
        print(f"✅ Найдено клиентов: {len(clients)}")
    except Exception as e:
        print(f"❌ Ошибка при загрузке клиентов: {e}")
        clients = []
    
    return render_template('admin/clients/list.html', clients=clients)

@admin_bp.route('/clients/add', methods=['GET', 'POST'])
def add_client():
    print("🔍 Доступ к форме добавления клиента...")
    from app.forms import ClientForm
    form = ClientForm()
    
    if form.validate_on_submit():
        try:
            client = Client(
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                phone=form.phone.data,
                email=form.email.data,
                notes=form.notes.data
            )
            db.session.add(client)
            db.session.commit()
            flash('Клиент успешно добавлен!', 'success')
            return redirect(url_for('admin.clients_list'))
        except Exception as e:
            flash(f'Ошибка: {str(e)}', 'error')
    
    return render_template('admin/clients/form.html', form=form, title='Добавление клиента')

@admin_bp.route('/clients/<int:id>/edit', methods=['GET', 'POST'])
def edit_client(id):
    print(f"🔍 Редактирование клиента {id}...")
    from app.forms import ClientForm
    try:
        client = Client.query.get_or_404(id)
        form = ClientForm(obj=client)
        
        if form.validate_on_submit():
            form.populate_obj(client)
            db.session.commit()
            flash('Данные клиента обновлены!', 'success')
            return redirect(url_for('admin.clients_list'))
        
        return render_template('admin/clients/form.html', form=form, title='Редактирование клиента')
    except Exception as e:
        flash(f'Ошибка: {str(e)}', 'error')
        return redirect(url_for('admin.clients_list'))

@admin_bp.route('/clients/<int:id>/delete', methods=['POST'])
def delete_client(id):
    print(f"🔍 Удаление клиента {id}...")
    try:
        client = Client.query.get_or_404(id)
        db.session.delete(client)
        db.session.commit()
        flash('Клиент успешно удален!', 'success')
    except Exception as e:
        flash(f'Ошибка: {str(e)}', 'error')
    
    return redirect(url_for('admin.clients_list'))

# ВРЕМЕННО ОТКЛЮЧАЕМ ВСЕ ОСТАЛЬНОЕ
@admin_bp.route('/appointments')
def appointments_list():
    return "Раздел записей - в разработке"

@admin_bp.route('/appointments/add')
def add_appointment():
    return "Форма записи - в разработке"

@admin_bp.route('/api/stats')
def api_stats():
    try:
        total_clients = Client.query.count()
    except:
        total_clients = 0
    
    return jsonify({
        'total_clients': total_clients,
        'total_appointments': 0,
        'today_appointments': 0
    })