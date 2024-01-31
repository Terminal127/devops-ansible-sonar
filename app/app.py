from flask import Flask, render_template, request, redirect, session, flash
from flask_pymongo import PyMongo
import redis

app = Flask(__name__)

# Set the MongoDB URI
app.config['MONGO_URI'] = 'mongodb://mongo:27017/testdb'  # Update with your actual URI

# Set the Redis URI
app.config['REDIS_URI'] = 'redis://redis:6379/0'  # Update with your actual URI

app.config['SECRET_KEY'] = 'your_secret_key'  # Change this to a strong secret key

mongo = PyMongo(app)
db = mongo.db
redis_db = redis.StrictRedis.from_url(app.config['REDIS_URI'])

if not redis_db.exists('admins'):
    redis_db.sadd('admins', 'admin')  # Add 'admin' as the initial admin username
if not redis_db.exists('admin'):
    redis_db.set('admin', 'adminpass')  # Set the password for the initial admin
# Check if the database exists, if not, create it
def create_database():
    try:
        mongo.db.command("serverStatus")
    except Exception as e:
        print(e)
        print("Database not present. Creating...")
        mongo.db.create_collection('employees')
        print("Database created.")

create_database()

@app.route('/')
def index():
    employees = db.employees.find()
    database_name = app.config['MONGO_URI'].split('/')[-1]  # Extract database name
    return render_template('index.html', employees=employees, database_name=database_name)

@app.route('/add', methods=['POST'])
def add_employee():
    create_database()  # Ensure the 'employees' collection and 'admins' set exist

    if request.method == 'POST':
        if 'username' not in session or session['username'] not in redis_db.smembers('admins'):
            flash("Unauthorized access. Please log in as admin.")
            return redirect('/')

        name = request.form['name']
        age = request.form['age']
        gender = request.form['gender']

        db.employees.insert_one({'name': name, 'age': age, 'gender': gender})

    return redirect('/')

@app.route('/drop', methods=['POST'])
def drop_table():
    if 'username' not in session or session['username'] not in redis_db.smembers('admins'):
        flash("Unauthorized access. Please log in as admin.")
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

@app.route('/login', methods=['GET','POST'])
def login():
    create_database()  # Ensure the initial admin username and password are set

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username and password:
            stored_password = redis_db.get(username)
            if stored_password and stored_password.decode('utf-8') == password:
                session['username'] = username
                flash(f"Logged in as {username}.")
                return redirect('/')
            else:
                flash("Invalid credentials. Please try again.")

    return render_template('login.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
