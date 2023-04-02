from flask import Flask, render_template, flash
import psycopg2
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import InputRequired, Length
import secrets

app = Flask(__name__)
secret_key = secrets.token_hex(16)
app.config['SECRET_KEY'] = secret_key

conn = psycopg2.connect(database="service_db",
                        user="postgres",
                        password="Vehjxrf1",
                        host="localhost",
                        port="5432")
cursor = conn.cursor()


class RegisterForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=2, max=80)],
                           render_kw={"placeholder": "Username"})
    name = StringField(validators=[InputRequired(), Length(min=2, max=80)],
                       render_kw={"placeholder": "Name"})
    password = StringField(validators=[InputRequired(), Length(min=2, max=80)],
                           render_kw={"placeholder": "Password"})
    submit = SubmitField("register")


class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=2, max=80)],
                           render_kw={"placeholder": "Username"})
    password = StringField(validators=[InputRequired(), Length(min=2, max=80)],
                           render_kw={"placeholder": "Password"})
    submit = SubmitField("login")


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        cursor.execute("SELECT * FROM service.users WHERE login=%s AND password=%s",
                       (str(username), str(password)))
        records = list(cursor.fetchall())
        if len(records) != 0:
            return render_template('account.html', full_name=records[0][1],
                                   login=records[0][2], password=records[0][3])
        else:
            flash("This user doesn't exist")

    return render_template('login.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        username = form.username.data
        name = form.name.data
        password = form.password.data

        cursor.execute(f"SELECT EXISTS(SELECT login FROM service.users WHERE login='{username}')")
        exist = cursor.fetchone()[0]
        if not exist:
            sql_query = "INSERT INTO service.users (full_name, login, password) VALUES (%s, %s, %s)"
            user_data = (name, username, password)

            cursor.execute(sql_query,user_data)
            conn.commit()


        else:
            flash("This username already exist")
    return render_template('register.html', form=form)

if __name__ == '__main__':
    app.run(debug=True)
