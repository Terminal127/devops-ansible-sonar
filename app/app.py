from flask import Flask, render_template, request, redirect, session, flash
from flask_pymongo import PyMongo
import redis
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)

# Set the MongoDB URI
app.config['MONGO_URI'] = 'mongodb://mongo:27017/testdb'  # Update with your actual URI

# Set the Redis URI
app.config['REDIS_URI'] = 'redis://redis:6379/0'  # Update with your actual URI

app.config['SECRET_KEY'] = 'your_secret_key'  # Change this to a strong secret key

mongo = PyMongo(app)
db = mongo.db
redis_db = redis.StrictRedis.from_url(app.config['REDIS_URI'])

# Check if the database 'users' exists, if not, create it
if not redis_db.exists('users'):
    redis_db.hset('users', 'anubhav', 'anubhav')  # Add 'anubhav' as the initial user with password 'anubhav'

# Check if the database exists, if not, create it
def create_database():
    try:
        # Check if 'employees' collection exists, if not, create it
        if 'employees' not in mongo.db.list_collection_names():
            mongo.db.create_collection('employees')
            print("Collection 'employees' created.")

    except Exception as e:
        print(e)
        print("Error creating database.")

create_database()

login_manager = LoginManager(app)
login_manager.login_view = 'login'

# User class for Flask-Login
class User(UserMixin):
    pass

@login_manager.user_loader
def load_user(user_id):
    user = User()
    user.id = user_id
    return user

@app.route('/')
@login_required
def index():
    employees = db.employees.find()
    database_name = app.config['MONGO_URI'].split('/')[-1]  # Extract database name
    return render_template('index.html', employees=employees, database_name=database_name)

@app.route('/add', methods=['POST'])
def add_employee():
    if 'username' not in session or session['username'] != 'anubhav':
        flash("Unauthorized access. Please log in as anubhav.")
        return redirect('/')

    name = request.form['name']
    age = request.form['age']
    gender = request.form['gender']

    db.employees.insert_one({'name': name, 'age': age, 'gender': gender})
    return redirect('/')

@app.route('/drop', methods=['POST'])
def drop_table():
    if 'username' not in session or session['username'] != 'anubhav':
        flash("Unauthorized access. Please log in as anubhav.")
        return redirect('/')

    db.employees.drop()
    return redirect('/')

@app.route('/search', methods=['POST'])
def search_employee():
    search_name = request.form['search_name']
    employees = db.employees.find({'name': search_name})

    if employees.count() == 0:
        message = f"No employee found with the name '{search_name}'."
    else:
        message = f"Employee(s) found with the name '{search_name}':"

    return render_template('index.html', employees=employees, message=message)

@app.route('/login', methods=['GET', 'POST'])
def login():
    create_database()

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        stored_password = redis_db.hget('users', username)

        if stored_password and stored_password.decode('utf-8') == password:
            user = User()
            user.id = username
            login_user(user)
            session['username'] = username
            flash(f"Logged in as {username}.")
            return redirect('/')

        flash("Invalid credentials. Please try again.")

    return render_template('login.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
