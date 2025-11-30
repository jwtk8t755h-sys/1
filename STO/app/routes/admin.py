from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app.models.clients import Client
from app.models.services import ServiceType
from app.models.employees import Employee
from app import db
from datetime import date

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/')
def dashboard():
    try:
        # Простая статистика без сложных запросов
        total_clients = Client.query.count()
        total_appointments = 0  # Пока не считаем
        today_appointments = 0  # Пока не считаем
        
        return render_template('admin/dashboard.html',
                             total_clients=total_clients,
                             total_appointments=total_appointments,
                             today_appointments=today_appointments)
    except Exception as e:
        flash(f'Ошибка загрузки дашборда: {str(e)}', 'error')
        return render_template('admin/dashboard.html',
                             total_clients=0,
                             total_appointments=0,
                             today_appointments=0)

@admin_bp.route('/clients')
def clients_list():
    try:
        clients = Client.query.all()
        return render_template('admin/clients/list.html', clients=clients)
    except Exception as e:
        flash(f'Ошибка загрузки клиентов: {str(e)}', 'error')
        return render_template('admin/clients/list.html', clients=[])

@admin_bp.route('/clients/add', methods=['GET', 'POST'])
def add_client():
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
            db.session.rollback()
            flash(f'Ошибка при добавлении клиента: {str(e)}', 'error')
    
    return render_template('admin/clients/form.html', form=form, title='Добавление клиента')

@admin_bp.route('/clients/<int:id>/edit', methods=['GET', 'POST'])
def edit_client(id):
    from app.forms import ClientForm
    client = Client.query.get_or_404(id)
    form = ClientForm(obj=client)
    
    if form.validate_on_submit():
        try:
            client.first_name = form.first_name.data
            client.last_name = form.last_name.data
            client.phone = form.phone.data
            client.email = form.email.data
            client.notes = form.notes.data
            
            db.session.commit()
            flash('Данные клиента обновлены!', 'success')
            return redirect(url_for('admin.clients_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка при обновлении клиента: {str(e)}', 'error')
    
    return render_template('admin/clients/form.html', form=form, title='Редактирование клиента', client=client)

@admin_bp.route('/clients/<int:id>/delete', methods=['POST'])
def delete_client(id):
    client = Client.query.get_or_404(id)
    try:
        db.session.delete(client)
        db.session.commit()
        flash('Клиент успешно удален!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Ошибка при удалении клиента: {str(e)}', 'error')
    
    return redirect(url_for('admin.clients_list'))

@admin_bp.route('/appointments')
def appointments_list():
    appointments = []
    return render_template('admin/appointments/calendar.html', appointments=appointments)

@admin_bp.route('/appointments/add')
def add_appointment():
    return "Форма записи - в разработке"

@admin_bp.route('/api/stats')
def api_stats():
    stats = {
        'total_clients': Client.query.count(),
        'total_appointments': 0,
        'today_appointments': 0,
        'pending_appointments': 0
    }
    return jsonify(stats)