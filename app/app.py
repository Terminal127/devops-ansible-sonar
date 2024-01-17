from flask import Flask, render_template, request, redirect
from flask_pymongo import PyMongo

app = Flask(__name__)

# Set the MongoDB URI
app.config['MONGO_URI'] = 'mongodb://mongo:27017/testdb'  # Update with your actual URI

mongo = PyMongo(app)
db = mongo.db
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
    return render_template('index.html', employees=employees)

@app.route('/add', methods=['POST'])
def add_employee():
    create_database()  # Ensure the 'employees' collection exists
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        gender = request.form['gender']

        db.employees.insert_one({'name': name, 'age': age, 'gender': gender})

    return redirect('/')

@app.route('/drop', methods=['POST'])
def drop_table():
    db.employees.drop()
    return redirect('/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)

