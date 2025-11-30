from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField, DateField
from wtforms.validators import DataRequired, Email, Length, Optional

class ClientForm(FlaskForm):
    first_name = StringField('Имя', validators=[DataRequired(), Length(min=2, max=50)])
    last_name = StringField('Фамилия', validators=[DataRequired(), Length(min=2, max=50)])
    phone = StringField('Телефон', validators=[DataRequired(), Length(min=5, max=20)])
    email = StringField('Email', validators=[Email(), Optional()])
    notes = TextAreaField('Примечания')
    submit = SubmitField('Сохранить')

class AppointmentForm(FlaskForm):
    client_id = SelectField('Клиент', coerce=int, validators=[DataRequired()])
    vehicle_id = SelectField('Автомобиль', coerce=int, validators=[DataRequired()])
    service_id = SelectField('Услуга', coerce=int, validators=[DataRequired()])
    employee_id = SelectField('Сотрудник', coerce=int, validators=[DataRequired()])
    appointment_date = DateField('Дата записи', format='%Y-%m-%d', validators=[DataRequired()])
    appointment_time = SelectField('Время', choices=[
        ('08:30', '08:30'), ('09:00', '09:00'), ('09:30', '09:30'),
        ('10:00', '10:00'), ('10:30', '10:30'), ('11:00', '11:00'),
        ('11:30', '11:30'), ('12:00', '12:00'), ('12:30', '12:30'),
        ('13:00', '13:00'), ('13:30', '13:30'), ('14:00', '14:00'),
        ('14:30', '14:30'), ('15:00', '15:00'), ('15:30', '15:30'),
        ('16:00', '16:00'), ('16:30', '16:30'), ('17:00', '17:00')
    ], validators=[DataRequired()])
    notes = TextAreaField('Примечания')
    submit = SubmitField('Записаться')