from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, IntegerField, FloatField, FileField, EmailField
from wtforms.fields.choices import SelectField
from wtforms.validators import DataRequired, URL, Length
from flask_ckeditor import CKEditorField

class RegisterForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    confirm = PasswordField("Confirm password", validators=[DataRequired()])
    submit = SubmitField("Register", render_kw={"class": "btn btn-light"})


# Create a form to login existing users
class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login", render_kw={"class": "btn btn-light"})


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
    first_name = StringField("First name", validators=[DataRequired()])
    second_name = StringField("Last name", validators=[DataRequired()])
    middle_name = StringField("Middle name(optional)", validators=[])
    email = EmailField("Email", validators=[DataRequired()])
    country_code = IntegerField("Country code?", validators=[DataRequired(), Length(min=1, max=3)])
    phone_number = IntegerField("Phone number?", validators=[DataRequired(), Length(min=7, max=10)])
    country = SelectField("Country", choices=[
                                                    ('NG', 'Nigeria'),
                                                    ('CA', 'Canada'),
                                                    ('MX', 'Mexico'),
                                                    ('US', 'United States'),
                                                    ('AR', 'Argentina'),
                                                    ('BR', 'Brazil'),
                                                    ('CO', 'Colombia'),
                                                    ('PE', 'Peru'),
                                                    ('FR', 'France'),
                                                    ('DE', 'Germany'),
                                                    ('IT', 'Italy'),
                                                    ('RU', 'Russia'),
                                                    ('ES', 'Spain'),
                                                    ('GB', 'United Kingdom'),
                                                    ('CN', 'China'),
                                                    ('IN', 'India'),
                                                    ('ID', 'Indonesia'),
                                                    ('JP', 'Japan'),
                                                    ('PK', 'Pakistan'),
                                                    ('SA', 'Saudi Arabia'),
                                                    ('KR', 'South Korea'),
                                                    ('TR', 'Turkey'),
                                                    ('EG', 'Egypt'),
                                                    ('ZA', 'South Africa'),
                                                    ('AU', 'Australia'),
                                                    ('NZ', 'New Zealand')
                                                ], validators=[DataRequired()])
    state = StringField("State", validators=[DataRequired()])
    city = StringField("City", validators=[DataRequired()])
    address = StringField("Address Line 1", validators=[DataRequired()])
    address2 = StringField("Address Line 2", validators=[])
    post_code = StringField("Postal code", validators=[DataRequired()])
    submit = SubmitField("Continue Checkout")

class GooglePay(FlaskForm):
    country_code = IntegerField("Country Code", validators=[DataRequired()])
    network = SelectField("Mobile network", choices=[("MTN", "MTN") , ("GLO", "GLO"), ("AIRTEL", "AIRTEL"), ("ETISALAT", "ETISALAT")], validators=[DataRequired()])
    phone_number = IntegerField("Phone number", validators=[DataRequired()])
    submit = SubmitField("Submit")

# elif charge_response.json()["data"]["next_action"]["type"] == "requires_additional_fields":
# url = f"https://api.flutterwave.cloud/developersandbox/charges/{search_response.json()['data'][0]['id']}"
# payload = {
#     "authorization": {
#         "type": "avs",
#         "avs": {
#             "address": {
#                 "city": "Gotham",
#                 "country": "US",
#                 "line1": "221B Baker Street",
#                 "line2": "Coker Estate",
#                 "postal_code": "94105",
#                 "state": "Colorado"
#             }
#         }
#     }
# }
# headers = {"X-Trace-Id": trace_id}
# response = requests.put(url, json=payload, headers=headers)
# print(response.text)