from flask import Flask, render_template, flash, redirect, url_for, session, request, logging

import pymysql
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('home1.html')

# About
@app.route('/about')
def about():
    return render_template('about.html')


# Register Form Class
class RegisterForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')

# User Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))
        db = pymysql.connect("localhost", "malli", "Malli@587", "flask")
        con = db.cursor()
        cursor = db.cursor()
        # Create cursor

        # Execute query
        cursor.execute("INSERT INTO users(name, email, username, password) VALUES(%s, %s, %s, %s)", (name, email, username, password))

        # Commit to DB
        db.commit()

        # Close connection
        cursor.close()



        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get Form Fields
        email = request.form['email']
        password_candidate = request.form['password']

        # Create cursor
        db = pymysql.connect("localhost", "malli", "Malli@587", "flask")
        con = db.cursor()
        cursor = db.cursor()

        # Get user by username
        result = cursor.execute("SELECT * FROM users WHERE email = %s", [email])

        if result > 0:
            # Get stored hash
            data = cursor.fetchone()

            password = data[-1]

            # Compare Passwords
            if sha256_crypt.verify(password_candidate, password):
                # Passed
                session['logged_in'] = True
                session['email'] = email

                return redirect(url_for('dashboard'))
            else:
                error = 'Invalid login'
                return render_template('login1.html', error=error)
            # Close connection
            cur.close()
        else:
            error = 'Username not found'
            return render_template('login1.html', error=error)

    return render_template('login1.html')

# Check if user logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('login'))
    return wrap

# Logout
@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))

# Dashboard
@app.route('/dashboard')
@is_logged_in
def dashboard():
    # Create cursor
    db = pymysql.connect("localhost", "malli", "Malli@587", "flask")
    con = db.cursor()
    cursor = db.cursor()


    result = cursor.execute("SELECT * FROM one WHERE email = %s", [session['email']])

    articles = cursor.fetchall()

    if result > 0:
        return render_template('dashboard.html', rows=articles)
    else:
        msg = 'No Data Found'
        return render_template('dashboard.html', msg=msg)
    # Close connection
    cur.close()
# Article Form Class
class ArticleForm(Form):
    Addamount = StringField('Addamount', [validators.Length(min=1, max=200)])

# Edit Article
@app.route('/edit_article/<string:id>', methods=['GET', 'POST'])
@is_logged_in
def edit_article(id):
    # Create cursor
    db = pymysql.connect("localhost", "malli", "Malli@587", "flask")
    con = db.cursor()
    cursor = db.cursor()

    # Get article by id
    result = cursor.execute("SELECT * FROM one WHERE id = %s", [id])

    article = cursor.fetchone()
    cursor.close()
    # Get form
    form = ArticleForm(request.form)

    # Populate article form fields
    form.Addamount.data = article[4]
    if request.method == 'POST' :
        Addamount = request.form['Addamount']


        # Create Cursor
        db = pymysql.connect("localhost", "malli", "Malli@587", "flask")
        con = db.cursor()
        cursor = db.cursor()
        app.logger.info(Addamount)
        # Execute
        cursor.execute ("UPDATE one SET Addamount=%s WHERE id=%s",(Addamount, id))
        # Commit to DB
        db.commit()

        #Close connection
        cursor.close()

        flash('Article Updated', 'success')

        return redirect(url_for('dashboard'))

    return render_template('edit_article.html', form=form)

if __name__ == '__main__':
    app.secret_key = 'secret123'
    app.run(debug=True,host='192.168.1.101',port=4000)
