from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, BooleanField, \
    TextAreaField, SelectField, IntegerField, FileField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired, Length


class RegisterForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired(), ])
    name = StringField('Имя', validators=[DataRequired()])
    surname = StringField('Фамилия', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль',
                                   validators=[DataRequired()])
    age = StringField('Возраст', validators=[DataRequired()])
    submit = SubmitField('Зарегистроваться')


class LoginForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class ProductAddForm(FlaskForm):
    name = StringField('Название товара', validators=[DataRequired()])
    count = IntegerField('Количество товара', validators=[DataRequired()])
    price = IntegerField('Цена товара', validators=[DataRequired()])
    by_who = StringField('Компания', validators=[DataRequired()])
    image = FileField('image', validators=[DataRequired()])
    category = SelectField('Категория',
                           validators=[DataRequired()])
    about = TextAreaField("О товаре", validators=[Length(max=32)])
    submit = SubmitField('Добавить')


class RoleUserForm(FlaskForm):
    name = StringField('Почта пользователя', validators=[])
    category = SelectField('Роль',
                           choices=['Администратор', 'Пользователь'],
                           validators=[DataRequired()])


class BuyForm(FlaskForm):
    count = IntegerField('Количество товара', validators=[DataRequired()])
