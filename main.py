from flask import Flask, abort, render_template, redirect, url_for, flash, request, jsonify
from flask_bootstrap import Bootstrap5
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user, login_required
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text, Float, Boolean
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from forms import RegisterForm, LoginForm, CommentForm, Add, EditItem
import os

app = Flask(__name__)
Bootstrap5(app)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
login_manager = LoginManager()
login_manager.init_app(app)
application = app
@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)


# For adding profile images to the comment section
# gravatar = Gravatar(app,
#                     size=100,
#                     rating='g',
#                     default='retro',
#                     force_default=False,
#                     force_lower=False,
#                     use_ssl=False,
#                     base_url=None)


# CREATE DATABASE
class Base(DeclarativeBase):
    pass

def clean(data):
    number = str(data)

    if "." in number:
        whole, decimal = number.split(".")
        whole = format(int(whole), ",")
        return f"{whole}.{decimal}"
    else:
        return format(int(number), ",")

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DB_STORE", "sqlite:///users.db")
db = SQLAlchemy(model_class=Base)
db.init_app(app)

class User(UserMixin, db.Model):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(100))
    cart = relationship("Cart", back_populates="user")



class Items(db.Model):
    __tablename__ = "stock"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), nullable=False)
    img_url: Mapped[str] = mapped_column(String(1250), nullable=True)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    price: Mapped[int] = mapped_column(Integer, nullable=False)
    unit: Mapped[str] = mapped_column(String(250), nullable=False)
    cart = relationship("Cart", back_populates="product")


class Cart(db.Model):
    __tablename__ = "cart"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("users.id"))
    item_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("stock.id"))
    amount: Mapped[int] = mapped_column(Integer, default=1)
    product = relationship("Items", back_populates="cart")
    user = relationship("User", back_populates="cart")



@app.route("/add-to-cart/<int:item_id>", methods=["POST"])
def add_to_cart(item_id):
    if not current_user.is_authenticated:
        return jsonify({
            'success': False,
            'message': 'You need to login or register to add item to cart! ️'
        }), 401

    try:
        already = db.session.execute(db.select(Cart).where(Cart.item_id == item_id)).scalar()
        if already:
           already.amount += 1
           db.session.commit()
        else:
            item_to_add = db.get_or_404(Items, item_id)
            new = Cart(product=item_to_add, user_id=current_user.id, item_id=item_id)
            db.session.add(new)
            db.session.commit()

        cart_count = len(current_user.cart)
        return jsonify({
            'success': True,
            'message': 'Item added to cart!',
            'cart_count': cart_count
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'An error occurred while adding the item.'
        }), 500


# class Cart(db.Model):
#     __tablename__ = "cart"
#     id: Mapped[int] = mapped_column(Integer, primary_key=True)
#     user_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("users.id"))
#     item_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("stock.id"))
#     amount: Mapped[int] = mapped_column(Integer, default=1)
#     item: Mapped[str] = mapped_column(String(250), nullable=False)
#     price: Mapped[float] = mapped_column(Float, nullable=False)
#     img_url: Mapped[str] = mapped_column(String(1250), nullable=True)
#     product = relationship("Items", back_populates="user")
#     user = relationship("User", back_populates="cart")


with app.app_context():
    db.create_all()


def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # If id is not 1 then return abort with 403 error
        if current_user.id != 1:
            return abort(403)
        # Otherwise continue with the route function
        return f(*args, **kwargs)

    return decorated_function

@app.route("/", methods=["GET", "POST"])
def home():
    stocks = db.session.execute(db.select(Items)).scalars().all()
    cart_count = len(current_user.cart) if current_user.is_authenticated else 0
    print(cart_count)
    return render_template("index.html", user=current_user, stocks=stocks, cart_count=cart_count)

@app.route('/register', methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():

        # Check if user email is already present in the database.
        result = db.session.execute(db.select(User).where(User.email == form.email.data))
        user = result.scalar()
        if user:
            flash("⚠️ You've already signed up with that email, log in instead!")
            return redirect(url_for('login'))

        if form.password.data != form.confirm.data:
            flash("⚠️ Passwords do not match.")
            return redirect(url_for('register'))

        hash_pw = generate_password_hash(form.password.data, method='pbkdf2:sha256', salt_length=8)
        new_user = User(
            email=form.email.data.lower(),
            name=form.name.data.title(),
            password=hash_pw
        )
        db.session.add(new_user)
        db.session.commit()
        # This line will authenticate the user with Flask-Login
        login_user(new_user)
        return redirect(url_for("home"))
    return render_template("register.html", form=form, current_user=current_user)


@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        password = form.password.data
        result = db.session.execute(db.select(User).where(User.email == form.email.data))
        # Note, email in db is unique so will only have one result.
        user = result.scalar()
        # Email doesn't exist
        if not user:
            flash("⚠️ That email does not exist, please try again.")
            return redirect(url_for('login'))
        # Password incorrect
        elif not check_password_hash(user.password, password):
            flash('⚠️ Password incorrect, please try again.')
            return redirect(url_for('login'))
        else:
            login_user(user)
            return redirect(url_for('home'))

    return render_template("login.html", form=form, current_user=current_user)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route("/add", methods=["GET", "POST"])
@admin_only
def add_new_item():
    cart_count = len(current_user.cart) if current_user.is_authenticated else 0
    print(cart_count)
    form = Add()
    if form.validate_on_submit():
        new_post = Items(
            name=form.name.data,
            description=form.description.data,
            price=form.price.data,
            img_url=form.img_url.data,
            unit=form.unit.data,

        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("add.html", form=form, current_user=current_user, cart_count=cart_count)

@app.route("/landing-page")
def landing():
    return render_template("landing.html")

@app.route('/checkout')
def cart():
    if not current_user.is_authenticated:
        flash("You need to login or register to add items to your cart.")
        return redirect(url_for("landing"))
    if current_user.is_authenticated:
        current_user_cart= db.session.execute(db.select(Cart).where(Cart.user_id == current_user.id)).scalars().all()
        cart_count = len(current_user.cart)
        prices = []
        for items in current_user_cart:
            price = items.amount * items.product.price
            prices.append(price)
        total = sum(prices)
        return render_template("cart.html", cart=current_user_cart, cart_count=cart_count, total=clean(total))

@app.route("/delete/<int:post_id>")
@admin_only
def delete(post_id):
    post_to_delete = db.get_or_404(Items, post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('home'))

@app.route("/delete-cart/<int:post_id>")
def delete_cart(post_id):
    post_to_delete = db.get_or_404(Cart, post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('cart'))

@app.route("/edit/<int:item_id>", methods=["GET", "POST"])
@admin_only
def edit_item(item_id):
    cart_count = len(current_user.cart) if current_user.is_authenticated else 0
    print(cart_count)
    form = db.get_or_404(Items, item_id)
    edit_form = EditItem(
        name=form.name,
        description=form.description,
        price=form.price,
        img_url=form.img_url,
        unit=form.unit,
    )
    if edit_form.validate_on_submit():
        form.name = edit_form.name.data
        form.description = edit_form.description.data
        form.price = edit_form.price.data
        form.img_url = edit_form.img_url.data
        form.unit = edit_form.unit.data
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("add.html", form=edit_form, is_edit=True, current_user=current_user, cart_count=cart_count)

@app.route("/search", methods=["GET", "POST"])
def search():
    cart_count = len(current_user.cart) if current_user.is_authenticated else 0
    searched = request.args.get('search').title()
    stock = db.session.execute(db.select(Items)).scalars().all()
    names = [item.name for item in stock]
    stocks = []
    for name in names:
        if searched in name:
            stocked = db.session.execute(db.select(Items).where(Items.name == name)).scalar()
            stocks.append(stocked)
    return render_template("search.html", user=current_user, stocks=stocks, cart_count=cart_count)

@app.route("/view/<int:item_id>")
def view(item_id):
    cart_count = len(current_user.cart) if current_user.is_authenticated else 0
    item = db.get_or_404(Items, item_id)
    return render_template("view.html", user=current_user, item=item, cart_count=cart_count)


@app.route("/inventory", methods=["GET", "POST"])
def inventory():
    stocks = db.session.execute(db.select(Items)).scalars().all()
    cart_count = len(current_user.cart) if current_user.is_authenticated else 0
    print(cart_count)
    return render_template("inventory.html", user=current_user, stocks=stocks, cart_count=cart_count)

if __name__ == "__main__":
    app.run(debug=True)

