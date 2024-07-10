from flask import Flask, request, session, redirect, url_for, render_template
import psycopg2
import bcrypt
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadTimeSignature
import os

app = Flask(__name__)
app.secret_key = 'kbajsdifgbijdbfkabibkabsi'  

conn = psycopg2.connect(database="flask_db",  
                        user="postgres", 
                        password="logi2002",  
                        host="localhost", port="5432") 

cursor = conn.cursor()

def create_users_table():
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(80) UNIQUE NOT NULL,
            email VARCHAR(120) UNIQUE NOT NULL,
            password VARCHAR(120) NOT NULL
        )
    ''')
    conn.commit()

create_users_table()

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'logithvikram.krishnamoorthy@vexternal.com'  
app.config['MAIL_PASSWORD'] = 'mixyzpgmfwbfqtnb'  
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False


mail = Mail(app)
s = URLSafeTimedSerializer(app.secret_key)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        hashed_password = hash_password(password)
        
        try:
            cursor.execute("SELECT * FROM users WHERE username = %s OR email = %s", (username, email))
            if cursor.fetchone():
                return redirect(url_for('register'))
            
            cursor.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)", (username, email, hashed_password.decode('utf-8')))
            conn.commit()
            
            return redirect(url_for('login'))
        
        except Exception as e:
            conn.rollback()
            return redirect(url_for('register'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        
        if user and bcrypt.checkpw(password.encode('utf-8'), user[3].encode('utf-8')):
            session['username'] = username
            return redirect(url_for('secure'))
       
    
    return render_template('login.html')

@app.route('/secure')
def secure():
    if 'username' in session:
        return render_template('secure.html')
    else:
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/reset_request', methods=['GET', 'POST'])
def reset_request():
    if request.method == 'POST':
        email = request.form['email']
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        
        if user:
            token = s.dumps(email, salt='password-reset-salt')
            link = url_for('reset_token', token=token, _external=True)
            
            msg = Message('Password Reset Request', sender='logithvikram.krishnamoorthy@vexternal.com', recipients=[email])
            msg.body = f'{link}'
            mail.send(msg)
            
            return redirect(url_for('login'))
        
    
    return render_template('reset_request.html')

@app.route('/reset_token/<token>', methods=['GET', 'POST'])
def reset_token(token):
    try:
        email = s.loads(token, salt='password-reset-salt', max_age=3600)
    except SignatureExpired:
        return redirect(url_for('reset_request'))
    except BadTimeSignature:
        return redirect(url_for('reset_request'))
    
    if request.method == 'POST':
        password = request.form['password']
        hashed_password = hash_password(password)
        
        cursor.execute("UPDATE users SET password = %s WHERE email = %s", (hashed_password.decode('utf-8'), email))
        conn.commit()
        
        return redirect(url_for('login'))
    
    return render_template('reset_token.html')

if __name__ == '__main__':
    app.run(debug=True)
