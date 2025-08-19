import ast
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

alien = AESEncryptor(encryption_key=encryption_key)


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


def token():
    url_1 = 'https://idp.flutterwave.com/realms/flutterwave/protocol/openid-connect/token'
    data_1 = {'client_id' : client_id, 'client_secret' : client_secret, 'grant_type': 'client_credentials'}
    response_1 = requests.post(url_1, data=data_1)
    access_token = response_1.json()["access_token"]
    return access_token



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
        already = db.session.execute(db.select(Cart).where(Cart.item_id == item_id, Cart.user_id == current_user.id)).scalar()
        if already:
           already.amount += 1
           db.session.commit()
        else:
            item_to_add = db.get_or_404(Items, item_id)
            new = Cart(product=item_to_add, user_id=current_user.id, item_id=item_id)
            db.session.add(new)
            db.session.commit()
        print(current_user.id)
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
    cart_count = len(current_user.cart) if current_user.is_authenticated else 0

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
    return render_template("register.html", form=form, current_user=current_user, cart_count=cart_count)


@app.route('/login', methods=["GET", "POST"])
def login():
    cart_count = len(current_user.cart) if current_user.is_authenticated else 0

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

    return render_template("login.html", form=form, current_user=current_user, cart_count=cart_count)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route("/add", methods=["GET", "POST"])
@admin_only
def add_new_item():
    cart_count = len(current_user.cart) if current_user.is_authenticated else 0

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


@app.route("/checkout", methods=["GET", "POST"])
def cart():
    transaction_reference = str(uuid.uuid4())
    trace_id = str(uuid.uuid4())
    idempotency_key = str(uuid.uuid4())
    access_token = token()
    bearer = f'Bearer {access_token}'
    url = "https://api.flutterwave.cloud/developersandbox/customers"

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
    else:
        cart_count = 0
        total = 0
        current_user_cart = 0
    if request.method == "POST":
        nonce = alien.generate_nonce(12)
        first_name = request.form.get("firstName")
        middle_name = request.form.get("middleName")
        last_name = request.form.get("lastName")
        if len(request.form.get("phone-number")) == 11:
            phone_number = request.form.get("phone-number")[1:]
        else:
            phone_number = request.form.get("phone-number")
        mail = request.form.get("email")
        address = request.form.get("address")
        address2 = request.form.get("address2")
        state = request.form.get("state")
        post_code = request.form.get("postCode")
        city = request.form.get("city")
        country_code = request.form.get("country_code")
        country = request.form.get("country")
        payment_option = request.form.get("paymentMethod")

        if payment_option == 'opay':
            required_fields = {
                "First Name": first_name,
                "Last Name": last_name,
                "Phone Number": phone_number,
                "Email": mail,
                "Address": address,
                "State": state,
                "Postal Code": post_code,
                "Country": country,
                "City": city,
                "Country Code": country_code,
                "Payment Option": payment_option,
                "nonce": nonce,
                "transaction_reference": transaction_reference
            }

        elif payment_option == "card":
            holder = alien.encrypt(request.form.get("cc-name"), nonce=nonce)
            cvv = alien.encrypt(request.form.get("cc-cvv"), nonce=nonce)
            expiration_month = alien.encrypt(request.form.get("cc-month"), nonce=nonce)
            expiration_year = alien.encrypt(request.form.get("cc-year"), nonce=nonce)
            cc_number = alien.encrypt(request.form.get("cc-number"), nonce=nonce)
            required_fields = {
                "First Name": first_name,
                "Last Name": last_name,
                "Phone Number": phone_number,
                "Email": mail,
                "Address": address,
                "State": state,
                "Postal Code": post_code,
                "Country": country,
                "City": city,
                "Country Code": country_code,
                "Payment Option": payment_option,
                "holder": holder,
                "cvv": cvv,
                "expiration_month": expiration_month,
                "expiration_year": expiration_year,
                "cc_number": cc_number,
                "nonce": nonce,
                "transaction_reference": transaction_reference
            }

        elif payment_option == "googlePay":
            holder = request.form.get("googlePay-card-holder")
            required_fields = {
                "First Name": first_name,
                "Last Name": last_name,
                "Phone Number": phone_number,
                "Email": mail,
                "Address": address,
                "State": state,
                "Postal Code": post_code,
                "Country": country,
                "City": city,
                "Country Code": country_code,
                "Payment Option": payment_option,
                "holder": holder,
                "nonce": nonce,
                "transaction_reference": transaction_reference
            }

        else:
            mobile = request.form.get("mobile_number")
            mobile_code = request.form.get("mobile_code")
            network = request.form.get("mobileMoney-network")
            required_fields = {
                "First Name": first_name,
                "Last Name": last_name,
                "Phone Number": phone_number,
                "Email": mail,
                "Address": address,
                "State": state,
                "Postal Code": post_code,
                "Country": country,
                "City": city,
                "Country Code": country_code,
                "Payment Option": payment_option,
                "mobile_code": mobile_code,
                "network": network,
                "mobile": mobile,
                "nonce": nonce,
                "transaction_reference": transaction_reference
            }
        for field_name, value in required_fields.items():
            if not value:
                flash(f"{field_name} is a required field.")
                return render_template("processing.html", cart_count=cart_count)

        credential_header = {'Authorization': bearer, "X-Idempotency-Key": idempotency_key, "X-Trace-Id": trace_id}
        if middle_name and address2:
            credential_data = {
                "address": {
                    "city": city,
                    "country": country,
                    "line1": address,
                    "line2": address2,
                    "postal_code": post_code,
                    "state": state
                },
                "name": {
                    "first": first_name,
                    "middle": middle_name,
                    "last": last_name
                },
                "phone": {
                    "country_code": country_code,
                    "number": phone_number
                },
                "email": mail}
        elif middle_name and not address2:
            credential_data = {
                "address": {
                    "city": city,
                    "country": country,
                    "line1": address,
                    "postal_code": post_code,
                    "state": state
                },
                "name": {
                    "first": first_name,
                    "middle": middle_name,
                    "last": last_name
                },
                "phone": {
                    "country_code": country_code,
                    "number": phone_number
                },
                "email": mail}
        elif address2 and not middle_name:
            credential_data = {
                "address": {
                    "city": city,
                    "country": country,
                    "line1": address,
                    "line2": address2,
                    "postal_code": post_code,
                    "state": state
                },
                "name": {
                    "first": first_name,
                    "last": last_name
                },
                "phone": {
                    "country_code": country_code,
                    "number": phone_number
                },
                "email": mail}
        else:
            credential_data = {
                "address": {
                    "city": city,
                    "country": country,
                    "line1": address,
                    "postal_code": post_code,
                    "state": state
                },
                "name": {
                    "first": first_name,
                    "last": last_name
                },
                "phone": {
                    "country_code": country_code,
                    "number": phone_number
                },
                "email": mail}
        try:
            search_url = 'https://api.flutterwave.cloud/developersandbox/customers/search'
            search_data = {'page': 1, 'size': 10, 'email': current_user.email}
            search_headers = {'Authorization': bearer, "X-Trace-Id": trace_id}
            search_response = requests.post(search_url, headers=search_headers, json=search_data)

        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'{e}'
            }), 500
        if search_response.json()['data']:
            update_url = f"https://api.flutterwave.cloud/developersandbox/customers/{search_response.json()['data'][0]['id']}"
            update = requests.put(url=update_url, headers=credential_header, json=credential_data)
            if update.json()["status"] == "success":
                return redirect(
                    url_for('pay', cacic=bearer, payment_option=payment_option, required_fields=required_fields,
                            track_id=trace_id, id_key=idempotency_key, total=total))
            else:
                return jsonify(update.json())
        else:
            credential_response = requests.post(url=url, headers=credential_header, json=credential_data)
            if credential_response.json()["status"] == "success":
                return redirect(
                    url_for('pay', cacic=bearer, payment_option=payment_option, required_fields=required_fields,
                            track_id=trace_id, id_key=idempotency_key, total=total))
            else:
                return jsonify(credential_response.json())
    return render_template("processing.html", cart=current_user_cart, cart_count=cart_count, total=clean(total))


@app.route("/payment", methods=["GET", "POST"])
def pay():
    prices = []
    current_user_cart = db.session.execute(db.select(Cart).where(Cart.user_id == current_user.id)).scalars().all()
    for items in current_user_cart:
        price = items.amount * items.product.price
        prices.append(price)
    total = sum(prices)
    method = request.args.get("payment_option")
    bearer = request.args.get("cacic")
    trace_id = request.args.get('track_id')
    idempotency_key = request.args.get('id_key')
    required_str = request.args.get("required_fields")
    required = ast.literal_eval(required_str)
    print(required)
    url = 'https://api.flutterwave.cloud/developersandbox/payment-methods'
    header = {'Authorization': bearer, 'X-Trace-Id': trace_id, 'X-Idempotency-Key': idempotency_key}
    try:
        search_url = 'https://api.flutterwave.cloud/developersandbox/customers/search'
        search_data = {'page': 1, 'size': 10, 'email': current_user.email}
        search_headers = {'Authorization': bearer, "X-Trace-Id": trace_id}
        search_response = requests.post(search_url, headers=search_headers, json=search_data)
        customer_id = search_response.json()['data'][0]['id']
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'{e}'
        }), 500

    if method == "card":
        data= {
        "type": "card",
        "card": {
            "encrypted_card_number": required["cc_number"],
            "encrypted_expiry_month": required["expiration_month"],
            "encrypted_expiry_year": required["expiration_year"],
            "encrypted_cvv": required["cvv"],
            "nonce": required["nonce"]}
        }
        response = requests.post(url=url, headers=header, json=data)
        if response.json()["status"] == "success":
            charge_url = 'https://api.flutterwave.cloud/developersandbox/charges'
            charge_header = {'Authorization': bearer, 'X-Trace-Id': trace_id, 'X-Idempotency-Key': idempotency_key}
            charge_data ={
            "reference": required["transaction_reference"],
            "currency": "NGN",
            "customer_id": customer_id,
            "payment_method_id": response.json()["data"]["id"],
            "redirect_url": "https://google.com",
            "amount": total,
            "meta": {
                "person_name": f'{required["First Name"]} {required["Last Name"]}',
                "role": "Developer"
                        }
                    }
            charge_response = requests.post(charge_url, headers=charge_header, json=charge_data)

            if charge_response.json()["data"]["next_action"]["type"] == "requires_otp":
                url = f"https://api.flutterwave.cloud/developersandbox/charges/{search_response.json()['data'][0]['id']}"
                payload = {
                                "authorization": {
                                    "type": "otp",
                                    "otp": {
                                        "code": "123456"
                                    }
                                }
                            }
                headers = {"X-Trace-Id": trace_id, "authorization": bearer}
                response = requests.put(url, json=payload, headers=headers)
                return jsonify(response.json())

            elif charge_response.json()["data"]["next_action"]["type"] == "requires_pin":
                url = f"https://api.flutterwave.cloud/developersandbox/charges/{search_response.json()['data'][0]['id']}"
                payload = {
                                "authorization": {
                                    "type": "pin",
                                    "pin": {
                                            "nonce": "w2zQDGCf1QXA",
                                            "encrypted_pin": "LC8FYIrkmK6oMULiBskRx9L3"
                                                                                        }
                                                                                    }
                            }
                headers = {"X-Trace-Id": trace_id, "authorization": bearer}
                response = requests.put(url, json=payload, headers=headers)
                return jsonify(response.json())

            elif charge_response.json()["data"]["next_action"]["type"] == "redirect_url":
                return redirect(url_for(charge_response.json()["data"]["next_action"]["redirect_url"]["url"]))

            else:
                return jsonify({
                    'success': False,
                    "message": charge_response.json()["data"]["next_action"]
                }), 500
        else:
            return jsonify(response.json())

    elif method == "mobileMoney":
        data= {
            "type": "mobile_money",
            "mobile_money": {
                "country_code": required["mobile_code"],
                "network": required["network"],
                "phone_number": required["mobile"]
            }
            }
        response = requests.post(url=url, headers=header, json=data)
        if response.json()["status"] == "success":
            charge_url = 'https://api.flutterwave.cloud/developersandbox/charges'
            charge_header = {'Authorization': bearer, 'X-Trace-Id': trace_id, 'X-Idempotency-Key': idempotency_key}
            charge_data ={
            "reference": required["transaction_reference"],
            "currency": "NGN",
            "customer_id": customer_id,
            "payment_method_id": response.json()["data"]["id"],
            "redirect_url": "https://google.com",
            "amount": total,
            "meta": {
                "person_name": f'{required["First Name"]} {required["Last Name"]}',
                "role": "Developer"
            }
        }
            charge_response = requests.post(charge_url, headers=charge_header, json=charge_data)
            if charge_response.json()["data"]["next_action"]["type"] == "requires_otp":
                url = f"https://api.flutterwave.cloud/developersandbox/charges/{search_response.json()['data'][0]['id']}"
                payload = {
                    "authorization": {
                        "type": "otp",
                        "otp": {
                            "code": "123456"
                        }
                    }
                }
                headers = {"X-Trace-Id": trace_id, "authorization": bearer}
                response = requests.put(url, json=payload, headers=headers)
                return jsonify(response.json())

            elif charge_response.json()["data"]["next_action"]["type"] == "requires_pin":
                url = f"https://api.flutterwave.cloud/developersandbox/charges/{search_response.json()['data'][0]['id']}"
                payload = {
                    "authorization": {
                        "type": "pin",
                        "pin": {
                            "nonce": "w2zQDGCf1QXA",
                            "encrypted_pin": "LC8FYIrkmK6oMULiBskRx9L3"
                        }
                    }
                }
                headers = {"X-Trace-Id": trace_id, "authorization": bearer}
                response = requests.put(url, json=payload, headers=headers)
                return jsonify(response.json())

            elif charge_response.json()["data"]["next_action"]["type"] == "redirect_url":
                return redirect(url_for(charge_response.json()["data"]["next_action"]["redirect_url"]["url"]))

            else:
                return jsonify({
                    'success': False,
                    "message": charge_response.json()["data"]["next_action"]
                }), 500
        else:
            return jsonify(response.json())
    elif method == "opay":
        data = {"type": "opay"}
        response = requests.post(url=url, headers=header, json=data)
        if response.json()["status"] == "success":
            charge_url = 'https://api.flutterwave.cloud/developersandbox/charges'
            charge_header = {'Authorization': bearer, 'X-Trace-Id': trace_id, 'X-Idempotency-Key': idempotency_key}
            charge_data = {
            "reference": required["transaction_reference"],
            "currency": "NGN",
            "customer_id": customer_id,
            "payment_method_id": response.json()["data"]["id"],
            "redirect_url": "https://google.com",
            "amount": total,
            "meta": {"person_name": f'{required["First Name"]} {required["Last Name"]}', "role": "Developer"}
            }
            print(charge_data)
            charge_response = requests.post(charge_url, headers=charge_header, json=charge_data)
            if charge_response.json()["data"]["next_action"]["type"] == "requires_otp":
                url = f"https://api.flutterwave.cloud/developersandbox/charges/{search_response.json()['data'][0]['id']}"
                payload = {
                    "authorization": {
                        "type": "otp",
                        "otp": {
                            "code": "123456"
                        }
                    }
                }
                headers = {"X-Trace-Id": trace_id, "authorization": bearer}
                response = requests.put(url, json=payload, headers=headers)
                return jsonify(response.json())

            elif charge_response.json()["data"]["next_action"]["type"] == "requires_pin":
                url = f"https://api.flutterwave.cloud/developersandbox/charges/{search_response.json()['data'][0]['id']}"
                payload = {
                    "authorization": {
                        "type": "pin",
                        "pin": {
                            "nonce": "w2zQDGCf1QXA",
                            "encrypted_pin": "LC8FYIrkmK6oMULiBskRx9L3"
                        }
                    }
                }
                headers = {"X-Trace-Id": trace_id, "authorization": bearer}
                response = requests.put(url, json=payload, headers=headers)
                return jsonify(response.json())

            elif charge_response.json()["data"]["next_action"]["type"] == "redirect_url":
                pay_rdr = charge_response.json()["data"]["next_action"]["redirect_url"]["url"]
                print(pay_rdr)
                return redirect(pay_rdr)

            else:
                return jsonify({
                    'success': False,
                    "message": charge_response.json()["data"]["next_action"]
                }), 500
        else:
            return jsonify(response.json())
    elif method == "googlePay":
        data = {"type":"googlepay",
                "googlepay":{
                    "card_holder_name": required["holder"]
                            }
                }
        response = requests.post(url=url, headers=header, json=data)
        if response.json()["status"] == "success":
            charge_url = 'https://api.flutterwave.cloud/developersandbox/charges'
            charge_header = {'Authorization': bearer, 'X-Trace-Id': trace_id, 'X-Idempotency-Key': idempotency_key}
            charge_data ={
            "reference": required["transaction_reference"],
            "currency": "NGN",
            "customer_id": customer_id,
            "payment_method_id": response.json()["data"]["id"],
            "redirect_url": "https://google.com",
            "amount": total,
            "meta": {
                "person_name": f'{required["First Name"]} {required["Last Name"]}',
                "role": "Developer"
            }
        }
            charge_response = requests.post(charge_url, headers=charge_header, json=charge_data)
            if charge_response.json()["data"]["next_action"]["type"] == "requires_otp":
                url = f"https://api.flutterwave.cloud/developersandbox/charges/{search_response.json()['data'][0]['id']}"
                payload = {
                    "authorization": {
                        "type": "otp",
                        "otp": {
                            "code": "123456"
                        }
                    }
                }
                headers = {"X-Trace-Id": trace_id, "authorization": bearer}
                response = requests.put(url, json=payload, headers=headers)
                return jsonify(response.json())

            elif charge_response.json()["data"]["next_action"]["type"] == "requires_pin":
                url = f"https://api.flutterwave.cloud/developersandbox/charges/{search_response.json()['data'][0]['id']}"
                payload = {
                    "authorization": {
                        "type": "pin",
                        "pin": {
                            "nonce": "w2zQDGCf1QXA",
                            "encrypted_pin": "LC8FYIrkmK6oMULiBskRx9L3"
                        }
                    }
                }
                headers = {"X-Trace-Id": trace_id, "authorization": bearer}
                response = requests.put(url, json=payload, headers=headers)
                return jsonify(response.json())

            elif charge_response.json()["data"]["next_action"]["type"] == "redirect_url":
                return redirect(url_for(charge_response.json()["data"]["next_action"]["redirect_url"]["url"]))

            else:
                return jsonify({
                    'success': False,
                    "message": charge_response.json()["data"]["next_action"]
                }), 500
        else:
            return jsonify(response.json())
    else:
        return jsonify({400 :{"Message": "Invalid Request"}})


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

#     try:
#         customer_list = requests.get(url, headers=headers, json=data)
#         print(f"Customer ID: {customer_list.json()['data'][0]['id']}")
#         print(customer_list.text)
#     except Exception as e:
#         return jsonify(e)