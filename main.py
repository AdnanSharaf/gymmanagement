import mysql.connector
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

# Database Configuration
MYSQL_HOST = 'localhost'
MYSQL_USER = 'root'
MYSQL_PASSWORD = 'mysql@123'
MYSQL_DB = 'gymmanagement'

# Connect to MySQL
db = mysql.connector.connect(
    host=MYSQL_HOST,
    user=MYSQL_USER,
    password=MYSQL_PASSWORD,
    database=MYSQL_DB
)
cursor = db.cursor()

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Added secret key for session management
login_manager = LoginManager()        # Added LoginManager for handling user sessions
login_manager.init_app(app)
login_manager.login_view = 'login'    # Redirect to login page if not logged in

class User(UserMixin):                   # User class for Flask-Login
    def __init__(self, id):
        self.id = id

@login_manager.user_loader             # User loader function for Flask-Login
def load_user(user_id):
    cursor.execute("SELECT * FROM Users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    if user:
        return User(id=user[0])
    return None

@app.route('/login', methods=['GET', 'POST'])  # New login route
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cursor.execute("SELECT * FROM Users WHERE username = %s", (username,))
        user = cursor.fetchone()
        
        if user and user[2] == password:  # Check password (consider hashing for production)
            user_obj = User(id=user[0])
            login_user(user_obj)
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password.')

    return render_template('login.html')  # Render login template

@app.route('/logout', methods=['POST'])                    # New logout route
@login_required                          # Ensure user is logged in
def logout():
    logout_user()                        # Log out the user
    return redirect(url_for('login'))   # Redirect to login page

@app.route('/')                          # Main index route
@login_required                          # Ensure user is logged in
def index():
    return render_template('index.html')

@app.route('/members')
def members():
    cursor.execute("SELECT * FROM Members")
    members_data = cursor.fetchall()
    return render_template('members.html', members_data=members_data)

@app.route('/insert_member', methods=['POST'])
def insert_member():
    if request.method == 'POST':
        name = request.form['name']
        contact_number = request.form['phone']
        email = request.form['email']
        membership_type = request.form['membership_type']
        start_date = request.form['join_date']

        sql = "INSERT INTO Members (name, contact_number, email, membership_type, start_date) VALUES (%s, %s, %s, %s, %s)"
        values = (name, contact_number, email, membership_type, start_date)

        cursor.execute(sql, values)
        db.commit()
        return redirect(url_for('members'))

@app.route('/trainers')
def trainers():
    cursor.execute("SELECT * FROM Trainers")
    trainers_data = cursor.fetchall()
    return render_template('trainers.html', trainers_data=trainers_data)

@app.route('/insert_trainer', methods=['POST'])
def insert_trainer():
    if request.method == 'POST':
        name = request.form['name']
        speciality = request.form['speciality']
        phone = request.form['Phone']

        sql = "INSERT INTO Trainers (name, speciality, Contact_number) VALUES (%s, %s, %s)"
        values = (name, speciality, phone)

        cursor.execute(sql, values)
        db.commit()
        return redirect(url_for('trainers'))

@app.route('/classes')
def classes():
    cursor.execute("SELECT * FROM Classes")
    classes_data = cursor.fetchall()
    return render_template('classes.html', classes_data=classes_data)

@app.route('/insert_class', methods=['POST'])
def insert_class():
    if request.method == 'POST':
        class_name = request.form['class_name']
        trainer_id = request.form['trainer_id']
        time = request.form['time']

        sql = "INSERT INTO Classes (class_name, trainer_id, time) VALUES (%s, %s, %s)"
        values = (class_name, trainer_id, time)

        cursor.execute(sql, values)
        db.commit()
        return redirect(url_for('classes'))

@app.route('/payments')
def payments():
    cursor.execute("SELECT * FROM Payments")
    payments_data = cursor.fetchall()
    return render_template('payments.html', payments_data=payments_data)

@app.route('/insert_payment', methods=['POST'])
def insert_payment():
    if request.method == 'POST':
        member_id = request.form['member_id']
        amount = request.form['amount']
        payment_date = request.form['payment_date']

        sql = "INSERT INTO Payments (member_id, amount, payment_date) VALUES (%s, %s, %s)"
        values = (member_id, amount, payment_date)

        cursor.execute(sql, values)
        db.commit()
        return redirect(url_for('payments'))

# Public view for classes and trainers
@app.route('/public')
def public_view():
    # Fetch classes and trainers without needing authentication
    cursor.execute("SELECT * FROM Classes")
    classes_data = cursor.fetchall()

    cursor.execute("SELECT * FROM Trainers")
    trainers_data = cursor.fetchall()

    return render_template('public_view.html', classes=classes_data, trainers=trainers_data)

if __name__ == '__main__':
    app.run(debug=True)

# Close the database connection
@app.teardown_appcontext
def close_db(error):
    if db.is_connected():
        db.close()
