import os
import psycopg2
from flask import Flask, render_template, request, redirect, session

app = Flask(__name__)

# Set the secret key for session management
app.secret_key = os.environ.get('SECRET_KEY', 'your_secret_key')

# Connect to the database
DATABASE_URL = os.environ.get('DATABASE_URL')
conn = psycopg2.connect(DATABASE_URL, sslmode='require')


@app.route('/')
def index():
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM register")
    myresult = cursor.fetchall()
    return render_template('index.html', myresult=myresult)


@app.route('/login')
def login_page():
    return render_template('login.html')


@app.route('/register')
def register_page():
    return render_template('register.html')


@app.route('/registerdone', methods=['GET', 'POST'])
def registerdone():
    if request.method == 'POST':
        # Get form data
        name = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # Check if email already exists in database
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM register WHERE email = %s", (email,))
        user = cursor.fetchone()

        if user:
            return 'Email address already registered'

        # Insert user data into database
        sql = "INSERT INTO register (name, email, password) VALUES (%s, %s, %s)"
        val = (name, email, password)
        cursor.execute(sql, val)
        conn.commit()

        # Redirect to the home page
        return render_template('registerdone.html', name=name)

    # If the request method is GET, render the register page
    return render_template('register.html')


@app.route('/logindone', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get form data
        email = request.form['email']
        password = request.form['password']

        # Check if email and password match database record
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM register WHERE email = %s AND password = %s", (email, password))
        user = cursor.fetchone()

        if user:
            # Create session for logged in user
            session['user_id'] = user[0]
            session['user_name'] = user[1]
            session['user_email'] = user[2]

            return redirect('/dashboard')
        else:
            return 'Invalid email or password'

    return render_template('login.html')


@app.route('/dashboard')
def dashboard():
    if 'user_id' in session:
        user_id = session['user_id']
        cursor = conn.cursor()

        # Check if table exists, create it if not
        cursor.execute(f"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = '{user_id}_web_orders')")
        if not cursor.fetchone()[0]:
            cursor.execute(f"CREATE TABLE {user_id}_web_orders (id SERIAL PRIMARY KEY, web_count INT, topic VARCHAR(255), order_date DATE, status VARCHAR(255))")

        cursor.execute(f'SELECT id, web_count, topic, order_date, status FROM {user_id}_web_orders')
        web_orders = cursor.fetchall()

        return render_template('dashboard.html', user_name=session['user_name'], user_email=session['user_email'], user_id=session['user_id'], web_orders=web_orders)
    else:
        return redirect('/login')


@app.route('/order_webs', methods=['POST'])
def order_webs():
    if 'user_id'


