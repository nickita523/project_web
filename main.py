from flask import Flask, render_template, redirect, request, session
from flask_login import LoginManager, login_user, login_required, logout_user, \
    current_user
from forms.user import *
from data.roles import Role
from data.user import User
from data.goods import Goods
from data.orders import Order
from data.categories import Categories
from data import db_session
import base64

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['UPLOADED_IMAGES_DEST'] = 'static/img'


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/register', methods=['GET', 'POST'])
def register():
    message_role = role_user()
    form_role = RoleUserForm()
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть",
                                   message_role=message_role,
                                   form_role=form_role
                                   )
        user = User(
            name=form.name.data,
            surname=form.surname.data,
            age=form.age.data,
            email=form.email.data,
            role=1,
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form,
                           message_role=message_role,
                           form_role=form_role)


@app.route('/login', methods=['GET', 'POST'])
def login():
    message_role = role_user()
    form_role = RoleUserForm()
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form,
                           message_role=message_role,
                           form_role=form_role)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    if 'cart' in session:
        session['cart'].clear()
    return redirect("/")


@app.route("/")
def index():
    return redirect("/magazin")


@app.route("/magazin/<id>/del")
def del_good(id):
    if current_user.is_authenticated:
        if current_user.role == 2:
            db_sess = db_session.create_session()
            good = db_sess.query(Goods).filter(
                Goods.name == id).first()
            if 'cart' in session:
                for j in session['cart']:
                    if good.name in j:
                        print(session)
                        session.modified = True
                        session['cart'].remove({good.name: j[good.name]})
            all_orders = db_sess.query(Order).all()
            for i in all_orders:
                for j in i.goods.split(';')[:-1]:
                    good_order = j[:j.find(':')]
                    print(good_order, good.id)
                    if int(good_order) == int(good.id):
                        db_sess.query(Order).filter(
                            Order.goods == i.goods).delete()
                        db_sess.commit()
            db_sess.query(Goods).filter(
                Goods.name == id).delete()
            db_sess.commit()
    return redirect('/magazin')


@app.route("/magazin/category/<category>", methods=['GET', 'POST'])
def main_page_category(category):
    form = RoleUserForm()
    db_sess = db_session.create_session()
    all_goods = db_sess.query(Goods).filter(
        Goods.category == category).all()
    images = []
    for i in all_goods:
        images.append(str(base64.b64encode(i.image).decode('utf8')))
    message = role_user()
    return render_template("main_page.html", all_goods=all_goods, images=images,
                           form_role=form, message_role=message)


@app.route("/magazin", methods=['GET', 'POST'])
def main_page():
    form = RoleUserForm()
    db_sess = db_session.create_session()
    all_goods = db_sess.query(Goods).all()
    images = []
    for i in all_goods:
        images.append(str(base64.b64encode(i.image).decode('utf8')))
    message = role_user()
    return render_template("main_page.html", all_goods=all_goods, images=images,
                           form_role=form, message_role=message)


def role_user():
    form = RoleUserForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(
                User.email == form.name.data).first():
            user = db_sess.query(User).filter(
                User.email == form.name.data).first()
            user.role = db_sess.query(Role).filter(
                Role.name == form.category.data).first().id
            db_sess.commit()
            message = 'Вы удачно сменили роль пользователя'
            return message
        else:
            message = 'Пользователь с таким именем не найден'
            return message
    return ''


@app.route("/magazin/<id>/buy", methods=['GET', 'POST'])
def buy_page(id):
    form = BuyForm()
    role_form = RoleUserForm()
    db_sess = db_session.create_session()
    all_goods = db_sess.query(Goods).all()
    good = db_sess.query(Goods).filter(
        Goods.name == id).first()
    message = role_user()
    images = []
    for i in all_goods:
        images.append(str(base64.b64encode(i.image).decode('utf8')))
    if current_user.is_authenticated:
        if form.validate_on_submit():
            if 'cart' in session:
                session.modified = True
                if good.count - form.count.data >= 0:
                    session['cart'].append({good.name: form.count.data})
                else:
                    return render_template("buy.html", all_goods=all_goods,
                                           images=images,
                                           form=form, good=good,
                                           message='Товара не хватает на складе',
                                           form_role=role_form,
                                           message_role=message)
            else:
                session['cart'] = [{good.name: form.count.data}]
            return redirect('/magazin')
        return render_template("buy.html", all_goods=all_goods, images=images,
                               form=form, good=good, form_role=role_form,
                               message_role=message)
    return render_template('main_page.html', all_goods=all_goods, images=images,
                           form=role_form, form_role=role_form,
                           message_role=message)


@app.route('/magazin/<id>/cart/del')
def cart_del(id):
    if current_user.is_authenticated:
        for i in session['cart']:
            for j in i:
                if j == id:
                    session.modified = True
                    session['cart'].pop(session['cart'].index(i))
    return redirect('/magazin/cart')


@app.route("/magazin/cart")
def cart_page():
    cart_goods = []
    form_role = RoleUserForm()
    count = []
    images = []
    db_sess = db_session.create_session()
    summ = 0
    if 'cart' in session:
        for i in session['cart']:
            print(session['cart'])
            for j in i:
                print(j)
                cart_goods.append(db_sess.query(Goods).filter(
                    Goods.name == j).first())
                count.append(i[j])
                summ += db_sess.query(Goods).filter(
                    Goods.name == j).first().price * int(i[j])
        for i in cart_goods:
            images.append(str(base64.b64encode(i.image).decode('utf8')))
    message_role = role_user()
    return render_template('cart.html', cart_goods=cart_goods, images=images,
                           sum=summ, count=count, form_role=form_role,
                           message_role=message_role)


@app.route("/add", methods=['GET', 'POST'])
def product_add():
    form = ProductAddForm()
    form_role = RoleUserForm()
    message_role = role_user()
    db_sess = db_session.create_session()
    form.category.choices = [i.name for i in
                             db_sess.query(Categories).all()]
    if current_user.is_authenticated and current_user.role == 2:
        if form.validate_on_submit():
            db_sess = db_session.create_session()
            if db_sess.query(Goods).filter(
                    Goods.name == form.name.data).first():
                return render_template('product_add.html', title='Регистрация',
                                       form=form,
                                       message="Такой товар уже существует",
                                       form_role=form_role,
                                       message_role=message_role)
            if request.files:
                image = request.files.get("image", None)
            good = Goods(
                name=form.name.data,
                count=form.count.data,
                price=form.price.data,
                category=db_sess.query(Categories).filter(
                    Categories.name == form.category.data).first().id,
                about=form.about.data,
                image=image.read(),
                by_who=form.by_who.data,
            )
            db_sess.add(good)
            db_sess.commit()
            return redirect("/")
        return render_template("product_add.html", form=form,
                               form_role=form_role,
                               message_role=message_role)
    else:
        return redirect("/")


@app.route("/magazin/cart/make")
def make_order():
    message_role = role_user()
    form_role = RoleUserForm()
    if current_user.is_authenticated:
        db_sess = db_session.create_session()
        summ = 0
        list_order = ''
        if 'cart' in session:
            if session['cart']:
                for good in session['cart']:
                    for name_good in good:
                        goods = db_sess.query(Goods).filter(
                            Goods.name == name_good).first()
                        summ += goods.price * int(good[name_good])
                        list_order += str(goods.id) + ':' + str(
                            good[name_good]) + ';'
                        goods.count = goods.count - int(good[name_good])
                        db_sess.commit()
                good = Order(
                    goods=list_order,
                    price=summ,
                    by_who=session['_user_id'],
                )
                db_sess.add(good)
                db_sess.commit()
                session['cart'].clear()
                session.modified = True
                return render_template('cart.html',
                                       message='Вы удачно заказали товары.',
                                       sum=0, form_role=form_role,
                                       message_role=message_role)
            else:
                return render_template('cart.html',
                                       message='У вас пустая корзина',
                                       sum=0, form_role=form_role,
                                       message_role=message_role)
        else:
            return render_template('cart.html',
                                   message='У вас пустая корзина',
                                   sum=0, form_role=form_role,
                                   message_role=message_role)
    else:
        return redirect('/')


@app.route('/orders')
def all_orders():
    html = []
    list_goods = []
    form_role = RoleUserForm()
    db_sess = db_session.create_session()
    list_orders = db_sess.query(Order).all()
    message_role = role_user()
    for order in list_orders:
        user = db_sess.query(User).filter(
            User.id == order.by_who).first().name
        for good in order.goods.split(';')[:-1]:
            count = good[good.find(':') + 1:]
            id_good = good[:good.find(':')]
            i = db_sess.query(Goods).filter(
                Goods.id == id_good).first()
            image = str(base64.b64encode(i.image).decode('utf8'))
            good_for_list = [i, count, image, user, order.price]
            list_goods.append(good_for_list)
        html.append({order.id: list_goods})
        list_goods = []
    return render_template('order.html', list_orders=html, form_role=form_role,
                           message_role=message_role)


def main():
    db_session.global_init("data/db/users.db")
    app.run(port=8070, host='127.0.0.1', debug=True)


if __name__ == '__main__':
    main()
