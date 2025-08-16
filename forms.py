from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, IntegerField, FloatField, FileField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditorField

class RegisterForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    confirm = PasswordField("Confirm password", validators=[DataRequired()])
    submit = SubmitField("Register", render_kw={"class": "btn btn-secondary"})


# Create a form to login existing users
class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login", render_kw={"class": "btn btn-secondary"})


# Create a form to add comments
class CommentForm(FlaskForm):
    comment_text = CKEditorField("Comment", validators=[DataRequired()])
    submit = SubmitField("Submit Comment")

class Add(FlaskForm):
    name = StringField("Name of item", validators=[DataRequired()])
    description = StringField("Description?", validators=[DataRequired()])
    img_url = StringField("Link to image", validators=[DataRequired(), URL()])
    price = FloatField("Price?", validators=[DataRequired()])
    unit = StringField("Unit of measurement?", validators=[DataRequired()])
    submit = SubmitField("Submit Item")

class EditItem(FlaskForm):
    name = StringField("Asset name", validators=[DataRequired()])
    description = StringField("Description?", validators=[DataRequired()])
    img_url = StringField("Link to image", validators=[DataRequired(), URL()])
    price = FloatField("Price?", validators=[DataRequired()])
    unit = StringField("Unit of measurement?", validators=[DataRequired()])
    submit = SubmitField("Edit")

class Cred(FlaskForm):
    name = StringField("Name of item", validators=[DataRequired()])
    description = StringField("Description?", validators=[DataRequired()])
    img_url = StringField("Link to image", validators=[DataRequired(), URL()])
    price = FloatField("Price?", validators=[DataRequired()])
    unit = StringField("Unit of measurement?", validators=[DataRequired()])
    submit = SubmitField("Submit Item")

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
#     <meta charset="UTF-8">
#     <meta name="viewport" content="width=device-width, initial-scale=1.0">
#     <title>CACIC SYNERGY</title>
#     {{ bootstrap.load_css() }}
#     <link
#       href="{{ url_for('static', filename='css/styles.css') }}"
#       rel="stylesheet"
#     />
#
#        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css">
#





# <form class="card p-2">
#           <div class="input-group">
#             <input type="text" class="form-control" placeholder="Promo code">
#             <button type="submit" class="btn btn-secondary">Redeem</button>
#           </div>
#         </form>
#       </div>
#       <div class="col-md-7 col-lg-8">
#         <h4 class="mb-3">Billing address</h4>
#         <form class="needs-validation" novalidate="">
#           <div class="row g-3">
#             <div class="col-sm-6">
#               <label for="firstName" class="form-label">First name</label>
#               <input type="text" class="form-control" id="firstName" placeholder="" value="" required="">
#               <div class="invalid-feedback">
#                 Valid first name is required.
#               </div>
#             </div>
#
#             <div class="col-sm-6">
#               <label for="lastName" class="form-label">Last name</label>
#               <input type="text" class="form-control" id="lastName" placeholder="" value="" required="">
#               <div class="invalid-feedback">
#                 Valid last name is required.
#               </div>
#             </div>
#
#             <div class="col-12">
#               <label for="username" class="form-label">Username</label>
#               <div class="input-group has-validation">
#                 <span class="input-group-text">@</span>
#                 <input type="text" class="form-control" id="username" placeholder="Username" required="">
#               <div class="invalid-feedback">
#                   Your username is required.
#                 </div>
#               </div>
#             </div>
#
#             <div class="col-12">
#               <label for="email" class="form-label">Email <span class="text-body-secondary">(Optional)</span></label>
#               <input type="email" class="form-control" id="email" placeholder="you@example.com">
#               <div class="invalid-feedback">
#                 Please enter a valid email address for shipping updates.
#               </div>
#             </div>
#
#             <div class="col-12">
#               <label for="address" class="form-label">Address</label>
#               <input type="text" class="form-control" id="address" placeholder="1234 Main St" required="">
#               <div class="invalid-feedback">
#                 Please enter your shipping address.
#               </div>
#             </div>
#
#             <div class="col-12">
#               <label for="address2" class="form-label">Address 2 <span class="text-body-secondary">(Optional)</span></label>
#               <input type="text" class="form-control" id="address2" placeholder="Apartment or suite">
#             </div>
#
#             <div class="col-md-5">
#               <label for="country" class="form-label">Country</label>
#               <select class="form-select" id="country" required="">
#                 <option value="">Choose...</option>
#                 <option>United States</option>
#               </select>
#               <div class="invalid-feedback">
#                 Please select a valid country.
#               </div>
#             </div>
#
#             <div class="col-md-4">
#               <label for="state" class="form-label">State</label>
#               <select class="form-select" id="state" required="">
#                 <option value="">Choose...</option>
#                 <option>California</option>
#               </select>
#               <div class="invalid-feedback">
#                 Please provide a valid state.
#               </div>
#             </div>
#
#             <div class="col-md-3">
#               <label for="zip" class="form-label">Zip</label>
#               <input type="text" class="form-control" id="zip" placeholder="" required="">
#               <div class="invalid-feedback">
#                 Zip code required.
#               </div>
#             </div>
#           </div>
#
#           <hr class="my-4">
#
#           <div class="form-check">
#             <input type="checkbox" class="form-check-input" id="same-address">
#             <label class="form-check-label" for="same-address">Shipping address is the same as my billing address</label>
#           </div>
#
#           <div class="form-check">
#             <input type="checkbox" class="form-check-input" id="save-info">
#             <label class="form-check-label" for="save-info">Save this information for next time</label>
#           </div>
#
#           <hr class="my-4">
#
#           <h4 class="mb-3">Payment</h4>
#
#           <div class="my-3">
#             <div class="form-check">
#               <input id="credit" name="paymentMethod" type="radio" class="form-check-input" checked="" required="">
#               <label class="form-check-label" for="credit">Credit card</label>
#             </div>
#             <div class="form-check">
#               <input id="debit" name="paymentMethod" type="radio" class="form-check-input" required="">
#               <label class="form-check-label" for="debit">Debit card</label>
#             </div>
#             <div class="form-check">
#               <input id="paypal" name="paymentMethod" type="radio" class="form-check-input" required="">
#               <label class="form-check-label" for="paypal">PayPal</label>
#             </div>
#           </div>
#
#           <div class="row gy-3">
#             <div class="col-md-6">
#               <label for="cc-name" class="form-label">Name on card</label>
#               <input type="text" class="form-control" id="cc-name" placeholder="" required="">
#               <small class="text-body-secondary">Full name as displayed on card</small>
#               <div class="invalid-feedback">
#                 Name on card is required
#               </div>
#             </div>
#
#             <div class="col-md-6">
#               <label for="cc-number" class="form-label">Credit card number</label>
#               <input type="text" class="form-control" id="cc-number" placeholder="" required="">
#               <div class="invalid-feedback">
#                 Credit card number is required
#               </div>
#             </div>
#
#             <div class="col-md-3">
#               <label for="cc-expiration" class="form-label">Expiration</label>
#               <input type="text" class="form-control" id="cc-expiration" placeholder="" required="">
#               <div class="invalid-feedback">
#                 Expiration date required
#               </div>
#             </div>
#
#             <div class="col-md-3">
#               <label for="cc-cvv" class="form-label">CVV</label>
#               <input type="text" class="form-control" id="cc-cvv" placeholder="" required="">
#               <div class="invalid-feedback">
#                 Security code required
#               </div>
#             </div>
#           </div>
#
#           <hr class="my-4">
#
#           <button class="w-100 btn btn-primary btn-lg" type="submit">Continue to checkout</button>
#         </form>