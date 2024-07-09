from flask import Flask, request, session, redirect, url_for, render_template
import psycopg2
import bcrypt

app = Flask(__name__)
app.secret_key = 'jashbaskbdgfikofnasfnoj' 

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
            password VARCHAR(120) NOT NULL
        )
    ''')
    conn.commit()

create_users_table()

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        hashed_password = hash_password(password)
        
        try:
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            if cursor.fetchone():
                return 'Username already exists'
            
            cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_password.decode('utf-8')))
            conn.commit()
            
            return redirect(url_for('login'))
        
        except Exception as e:
            conn.rollback()
            return f'Error: {str(e)}'
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        
        if user and bcrypt.checkpw(password.encode('utf-8'), user[2].encode('utf-8')):
            session['username'] = username  
            return redirect(url_for('secure'))
        else:
            return 'Login failed'
    
    return render_template('login.html')

@app.route('/')
def route():
    return render_template('index.html')

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


if __name__ == '__main__':
    app.run(debug=True)
