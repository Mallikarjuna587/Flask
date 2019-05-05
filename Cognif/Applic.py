from flask import Flask, render_template, flash, redirect, url_for, session, request, logging

import pymysql
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps
import getpass
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
import matplotlib.pyplot as plt; plt.rcdefaults()
import numpy as np
import matplotlib.pyplot as plt

msg = MIMEMultipart()
msg['From'] = 'kmallikarjuna183@gmail.com'
msg['To'] = 'kmallikarjuna587@gmail.com'
msg['Subject'] = 'Amount has been updated'
msg['CC'] = 'kmallikarjuna183@gmail.com'

pic = os.path.join('static', 'pic')
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = pic
def database():
    db = pymysql.connect("localhost", "malli", "Malli@587", "flask")
    con = db.cursor()
    cursor = db.cursor()
    return cursor
@app.route('/')
def index():
    return render_template('/home1.html')

@app.route('/home')
def home():
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
    error = None
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['Username']
        password = sha256_crypt.encrypt(str(request.form['password']))
        db = pymysql.connect("localhost", "malli", "Malli@587", "flask")
        con = db.cursor()
        cursor = db.cursor()
        # Create cursor
        s = cursor.execute("SELECT email FROM users WHERE email = %s", [email])
        if s > 0:
            if request.form['email'] == cursor.fetchone()[0]:
                error = 'Email already exist! '
                return render_template('register.html', error=error)
        else:
            cursor.execute("INSERT INTO users(email, username, password) VALUES(%s, %s, %s)",
                       (email, username, password))
            db.commit()
            cursor.close()
            return redirect(url_for('login'))
    return render_template('register.html',error = error)


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
            return redirect(url_for('login1'))

    return wrap


# Logout
@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    # flash('You are now logged out', 'success')
    return redirect(url_for('home'))


# Dashboard
@app.route('/dashboard')
def dashboard():
    # Create cursor
    db = pymysql.connect("localhost", "malli", "Malli@587", "flask")
    con = db.cursor()
    cursor = db.cursor()
    cursor.execute("SELECT Username FROM expense WHERE Email = %s", [session['email']])
    name = cursor.fetchone()[0]
    result = cursor.execute("SELECT * FROM expense WHERE Email = %s", [session['email']])

    rows = cursor.fetchall()

    if result > 0:
        full_filename = os.path.join(app.config['UPLOAD_FOLDER'], 'analysis.png')
        piechart = os.path.join(app.config['UPLOAD_FOLDER'], 'piechart.png')
        return render_template('dashboard.html', rows=rows,name = name,user_image=full_filename,piechart = piechart)
    else:
        msg = 'No Data Found'
        return render_template('dashboard.html', msg=msg)
    # Close connection
    cur.close()

def decrypt(message):
    passwd=''
    for i in message:
        passwd=passwd+chr(ord(i)-2)
    return passwd
@app.route('/update/<string:id>', methods=['GET', 'POST'])
@is_logged_in
def update(id):
    if request.method == 'POST':
        Addamount = request.form['AddAmount']
        comment = request.form['comment']
        # Create Cursor
        db = pymysql.connect("localhost", "malli", "Malli@587", "flask")
        con = db.cursor()
        cursor = db.cursor()
        cursor.execute('select Amount_paid,pending_amount,Total_amount_spent,Username from expense where ID=%s',(id))
        t = cursor.fetchall()[0]
        ap = t[0]+float(Addamount)
        pa = t[2]- ap
        name = t[3]
        ta = t[2]
        cursor.execute("UPDATE expense SET Amount_paid=%s,pending_amount =%s,comment = %s WHERE ID=%s", (ap,pa,comment,id))
        # Commit to DB
        db.commit()
        # Close connection
        cursor.close()
        flash('Updated', 'success')

        message = 'Hi {}\n\n Hope you are doing Good!\n\n You paid ${} and your current pending amount is ${} ' \
                  ' \n\nThanks \nMallik'.format(name,Addamount,pa)
        msg.attach(MIMEText(message, 'plain'))
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login("kmallikarjuna183@gmail.com", decrypt('OcnnkB7:9'))
        server.sendmail('kmallikarjuna183@gmail.com', 'kmallikarjuna587@gmail.com', msg.as_string())

        objects = ('Total Amount Spent', 'Amount Paid', 'Pending Amount')
        labels = ('Pending amount', 'Amount paid')
        values = [pa, ap]
        colors = ['red', 'green']
        plt.title('Amount paid vs Pending amount')
        plt.pie(values, labels=labels, colors=colors, autopct='%1.1f%%', shadow=True, startangle=140)
        plt.savefig('C:/Users/kmall/PycharmProjects/new1/static/pic/piechart.png')
        plt.close()
        y_pos = np.arange(len(objects))
        values = [ta, ap, pa]
        plt.bar(y_pos, values, align='center', alpha=0.5)
        plt.xticks(y_pos, objects)
        for i, v in enumerate(values):
            plt.text(y_pos[i] - 0.25, v + 0.01, str(v))
        plt.ylabel('Amount')
        plt.title('Analysis')
        plt.savefig('C:/Users/kmall/PycharmProjects/new1/static/pic/analysis.png')
        return redirect(url_for('dashboard'))
    return render_template('dashboard.html')
@app.route('/MyTeamExpense', methods=['GET', 'POST'])
def MyTeamExpense():
    # Create cursor
    db = pymysql.connect("localhost", "malli", "Malli@587", "flask")
    con = db.cursor()
    cursor = db.cursor()
    cursor.execute("SELECT Username FROM expense WHERE Email = %s", [session['email']])
    name = cursor.fetchone()[0]

    result = cursor.execute("SELECT * FROM expense WHERE supervioser_email = %s", [session['email']])

    rows = cursor.fetchall()
    if result > 0:
        full_filename = os.path.join(app.config['UPLOAD_FOLDER'], 'analysis.png')
        piechart = os.path.join(app.config['UPLOAD_FOLDER'], 'piechart.png')
        return render_template('MyTeamExpense.html', rows=rows, name=name,user_image=full_filename,piechart = piechart)
    else:
        msg = 'No Data Found'
        return render_template('MyTeamExpense.html', msg=msg)
    # Close connection
    cur.close()

if __name__ == '__main__':
    app.secret_key = 'secret123'
    app.run(debug=True,host = '192.168.0.106', port=8000)
