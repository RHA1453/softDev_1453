from app import app
from flask import render_template, request, redirect, session
from flask_wtf import FlaskForm, Form
from wtforms import validators, StringField, SubmitField, SelectField, FormField
from flask_mysqldb import MySQL
from cerberus import Validator
from flask_bcrypt import Bcrypt

app.config['SECRET_KEY'] = 'redishketch'
mysql = MySQL(app)
bcrypt = Bcrypt(app)

@app.route('/')
def index():
    return render_template('index.html')
@app.route('/article')
def article():
    return render_template('./Pages/Article.html')
@app.route('/login')
def login():
    return render_template('./Auth/login.html')
@app.route('/signup')
def signup():
    return render_template('./Auth/signup.html')
@app.route('/sb')
def sb():
    return redirect ('https://www.facebook.com/')


@app.route('/api/user/login', methods=["POST"])
def login_api():
    INPUT = request.form
    v = Validator()
    schema = {
        'email': {'type': 'string', 'required': True},
        'password': {'type': 'string', 'required': True},
    }
    if v.validate(INPUT, schema) == False:
        return {"status":  5000, "msg": "validation error", "errors": v.errors}

    try:
        cur = mysql.connection.cursor()
        cur.execute("""SELECT * FROM users WHERE email = %s""", [INPUT['email']])
        user = cur.fetchone()
        if user is None:
            return {"status":  5000, "msg": "validation error", "errors": {"email": ["Email address doesn't exist"]}}
        if bcrypt.check_password_hash(user['password'], INPUT['password']) == False:
            return {"status":  5000, "msg": "validation error", "errors": {"password": ["invalid credential, Please check"]}}
        else:
            session['__auth__'] = user
            session_user = session.get('__auth__')
            return {"status":  2000, "msg": "login successful", "user": session_user}
    except Exception as e:
        return {"status":  5000, "msg": "something went wrong", "error": str(e)}


@app.route('/api/user/logout', methods=["POST"])
def logout_api():
    session.pop('__auth__')
    return {"status":  2000, "msg": "logout successful"}

@app.route('/api/user/register', methods=["POST"])
def register_api():
    INPUT = request.form
    v = Validator()
    schema = {
        'name': {'type': 'string', 'required': True},
        'username': {'type': 'string', 'required': True},
        'institute': {'type': 'string', 'required': True},
        'phone': {'type': 'string', 'required': True},
        'email': {'type': 'string', 'required': True},
        'password': {'type': 'string', 'required': True},
        'confirm_password': {'type': 'string', 'required': True},
    }
    if v.validate(INPUT, schema) == False:
        return {"status":  5000, "msg": "validation error", "errors": v.errors}

    if INPUT['password'] != INPUT['confirm_password']:
        return {"status":  5000, "msg": "validation error", "errors": {"password": ["Confirm password did not match"]}}

    cur = mysql.connection.cursor()
    cur.execute("""SELECT * FROM users WHERE email = %s""", [INPUT['email']])
    user = cur.fetchone()

    if user is not None:
        return {"status":  5000, "msg": "validation error", "errors": {"email": ["Email address already exist"]}}

    password_hashed = bcrypt.generate_password_hash(INPUT['password'])
    try:
        cur.execute("INSERT INTO users (name, username, institute, phone, email, password) VALUES (%s,%s,%s,%s,%s,%s)", (INPUT['name'], INPUT['username'], INPUT['institute'], INPUT['phone'], INPUT['email'], password_hashed))
        mysql.connection.commit()
        return {"status":  2000, "msg": "successfully registered"}
    except Exception as e:
        return {"status":  5000, "msg": "something went wrong", "error": str(e)}



