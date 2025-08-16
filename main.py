from os import access

from flask import Flask, abort, render_template, redirect, url_for, flash, request, jsonify
from flask_bootstrap import Bootstrap5
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user, login_required
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text, Float, Boolean
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from forms import RegisterForm, LoginForm, CommentForm, Add, EditItem
import requests
import base64
import secrets
import string
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os
import uuid


app = Flask(__name__)
Bootstrap5(app)
client_id = "c00c4196-adc1-4976-aac5-d591a78542ff"
client_secret = "tQEKaUHsxf2J833xWpwyJLyjpcXuqwhH"
encryption_key = "jQAOttdsQO+jH6pVr1ANW1HTHAOpeP5uTxMFaj2S/CE="
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
login_manager = LoginManager()
login_manager.init_app(app)
application = app
@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)



class AESEncryptor:
    def __init__(self, encryption_key: str):
        self.aes_key = base64.b64decode(encryption_key)

    @staticmethod
    def generate_nonce(length: int = 12) -> str:
        characters = string.ascii_letters + string.digits
        return ''.join(secrets.choice(characters) for _ in range(length))

    def encrypt(self, plain_text: str, nonce: str) -> str:
        if not plain_text or not nonce:
            raise ValueError('Both plain_text and nonce are required for encryption.')

        nonce_bytes = nonce.encode()
        aes_gcm = AESGCM(self.aes_key)
        cipher_text = aes_gcm.encrypt(nonce_bytes, plain_text.encode(), None)

        return base64.b64encode(cipher_text).decode()

    def encrypt_dict(self, data: dict) -> dict:
        if not isinstance(data, dict):
            raise ValueError("Data must be a dictionary.")

        nonce = self.generate_nonce()
        encrypted_data = {"nonce": nonce}

        for key, value in data.items():
            encrypted_data[key] = self.encrypt(str(value), nonce)

        return encrypted_data


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

inventory_dict = [{
        "description": "Made through controlled heating, blending, filtration and extraction. With no added colouring or preservatives it is a natural sugar that has the added benefit of being less processed than white sugar.",
        "id": 1,
        "img_url": "https://skinnyms.com/wp-content/uploads/2021/03/Homemade-Date-Syrup-1-Yum-500x500.jpg",
        "name": "Date Syrup",
        "price": 15000.0,
        "unit": "Litre"
    },
    {
        "description": "Made through controlled heating, blending, filtration and extraction. With no added colouring or preservatives it's a natural sugar that has the added benefit of being less processed than white sugar.",
        "id": 2,
        "img_url": "https://m.media-amazon.com/images/I/713rSxKKaPL.jpg",
        "name": "Date Syrup ",
        "price": 7000.0,
        "unit": "50CL"
    },
    {
        "description": "Vacum dried fresh catfish, selectively sorted and dried under the perfect temperature, humidty and atmosphere to ensure the nutritional and hygenic qualities were maintained.",
        "id": 3,
        "img_url": "https://sc04.alicdn.com/kf/A83b0a6b2eb864b9d9fe9023c946cc3b8T.jpg",
        "name": "Cat Fish",
        "price": 5000.0,
        "unit": "KG"
    },
    {
        "description": "Get value and quality with our 50 kg bag of rice. Ideal for bulk buying, this premium rice is perfect for everyday meals, catering, or large family.",
        "id": 4,
        "img_url": "https://mall.thecbncoop.com/assets/images/products/1634569714Mama-choice---50-420x458.jpg",
        "name": "Bag of Rice",
        "price": 80500.0,
        "unit": "50KG"
    },
    {
        "description": "Vegetable oil locally produced in Nigeria, well filtered, available in 25L kegs, hygienically packaged, and has a tamper-evident seal",
        "id": 5,
        "img_url": "https://deeski.com/image/cache/catalog/Foods/Kings%20devon%20veg%20oil%2025ltrs-500x500.jpg",
        "name": "Groundnut Oil",
        "price": 90500.0,
        "unit": "25Litre"
    },
    {
        "description": "Palm oil locally produced in Nigeria, well filtered, available in 25L kegs, hygienically packaged, and has a tamper-evident seal",
        "id": 6,
        "img_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcT6YNYp1jJXMOynawoAtkgEpaqOgtf9NOfcRQ&s",
        "name": "Palm Oil",
        "price": 68500.0,
        "unit": "25Litre"
    }]

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
    if stocks:
        cart_count = len(current_user.cart) if current_user.is_authenticated else 0
        return render_template("index.html", user=current_user, stocks=stocks, cart_count=cart_count, page='Products')
    else:
        cart_count = len(current_user.cart) if current_user.is_authenticated else 0
        return render_template("index.html", user=current_user, stocks=inventory_dict, cart_count=cart_count, page='This Is a Demo Product Page - current inventory Database is empty')


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

@app.route('/cart')
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

@app.route("/checkout", methods=["GET", "POST"])
def checkout():
    trace_id = str(uuid.uuid4())
    idempotency_key = str(uuid.uuid4())
    access_token = token()

    bearer = f'Bearer {access_token}'
    credential_url = 'https://api.flutterwave.cloud/developersandbox/customers'
    credential_header = {'Authorization' : bearer, "X-Idempotency-Key": idempotency_key, "X-Trace-Id": trace_id}
    credential_data = {
    "address": {
        "city": "Gotham",
        "country": "US",
        "line1": "221B Baker Street",
        "line2": "b",
        "postal_code": "94105",
        "state": "Colorado"
    },
    "name": {
        "first": "King",
        "middle": "Leo",
        "last": "James"
    },
    "phone": {
        "country_code": "1",
        "number": "6313958745"
    },
    "email": "james@example.com"}

    credential_response = requests.post(url=credential_url, headers=credential_header, json=credential_data)
    print(credential_response)
    # card_url = 'https://api.flutterwave.cloud/developersandbox/payment-methods'
    # card_header = { 'Authorization': 'Bearer {{YOUR_ACCESS_TOKEN}}', 'Content-Type': 'application/json', 'X-Trace-Id': '{{YOUR_UNIQUE_TRACE_ID}}', 'X-Idempotency-Key': '{{YOUR_UNIQUE_INDEMPOTENCY_KEY}}'}
    # data= {
    # "type": "card",
    # "card": {
    #     "encrypted_card_number": "{{$encrypted_card_number}}",
    #     "encrypted_expiry_month": "{{$encrypted_expiry_month}}",
    #     "encrypted_expiry_year": "{{$encrypted_expiry_year}}",
    #     "encrypted_cvv": "{{$encrypted_cvv}}",
    #     "nonce": "{{$randomly_generated_nonce}}"}
    # }
    # response = requests.post(url=card_url, headers=card_header, data=data)
    return jsonify(credential_response.json())

def token():
    url_1 = 'https://idp.flutterwave.com/realms/flutterwave/protocol/openid-connect/token'
    data_1 = {'client_id' : client_id, 'client_secret' : client_secret, 'grant_type': 'client_credentials'}
    response_1 = requests.post(url_1, data=data_1)
    access_token = response_1.json()["access_token"]
    return access_token


@app.route("/delete/<int:post_id>")
@admin_only
def delete(post_id):
    post_to_delete = db.get_or_404(Items, post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('inventory'))

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
        return redirect(url_for("inventory"))
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

