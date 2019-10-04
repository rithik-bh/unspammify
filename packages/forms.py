from wtforms import Form, validators, StringField, PasswordField
from wtforms.fields.html5 import DateField


class LoginForm(Form):
    user_id = StringField(
        '', [validators.DataRequired()], render_kw={'autofocus': True, 'placeholder': 'Username'})
    password = PasswordField('', [validators.DataRequired()], render_kw={
                             'placeholder': 'Password'})


class RegisterForm(Form):
    first_name = StringField(
        '', [validators.Length(max=20), validators.DataRequired()], render_kw={'autofocus': True, 'placeholder': 'First Name'})
    last_name = StringField(
        '', [validators.Length(max=20), validators.DataRequired()], render_kw={'placeholder': 'Last Name'})
    user_id = StringField(
        '', [validators.Length(min=2, max=10), validators.DataRequired()], render_kw={'placeholder': 'University ID'})
    password = PasswordField('', [validators.Length(
        min=5), validators.DataRequired()], render_kw={'placeholder': 'Password'})


class AddEvent(Form):
    date = DateField('', [validators.DataRequired()], render_kw={
                     'autofocus': True, 'placeholder': 'Event Date ?'})
    venue = StringField('', [validators.DataRequired()], render_kw={
                        'placeholder': 'Event Venue'})
    time = StringField('', [validators.DataRequired()],
                       render_kw={'placeholder': 'Event Time'})
    description = StringField('', [validators.DataRequired()], render_kw={
                              'placeholder': 'Event Description'})


class AdminLogin(Form):
    password = PasswordField('', [validators.DataRequired()], render_kw={
                             'autofocus': True, 'placeholder': 'Password'})


class ModifyEvent(Form):
    date = DateField('', [validators.DataRequired()], render_kw={
        'autofocus': True, 'placeholder': 'Event Date ?'})
    venue = StringField('', [validators.DataRequired()], render_kw={
                        'placeholder': 'Event Venue'})
    time = StringField('', [validators.DataRequired()],
                       render_kw={'placeholder': 'Event Time'})
    description = StringField('', [validators.DataRequired()], render_kw={
                              'placeholder': 'Event Description'})
