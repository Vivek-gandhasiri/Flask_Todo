from flask import Flask, jsonify, request, render_template, redirect, url_for, make_response
from flask_pymongo import PyMongo
from pymongo import MongoClient
from bson import ObjectId
from flask_login import LoginManager, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps
import logging
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Vivek@123'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/Flask_Database'  # Replace with your MongoDB URI
mongo = PyMongo(app)

client = MongoClient('mongodb://localhost:27017/')
db = client['Flask_Database']
users_collection = db['users']
tasks_collection = db['tasks']

# Configure logging
logging.basicConfig(level=logging.DEBUG)

login_manager = LoginManager(app)

@login_manager.user_loader
def load_user(user_id):
    try:
        return mongo.db.users.find_one({"_id": ObjectId(user_id)})
    except Exception as e:
        logging.error(f'Error loading user: {str(e)}')
        return None

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.cookies.get('token')  # Adjust based on how token is sent

        if not token:
            return jsonify({'message': 'Token is missing'}), 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = mongo.db.users.find_one({'_id': ObjectId(data['user_id'])})

            if not current_user:
                return jsonify({'message': 'User not found'}), 401

        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token is expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token'}), 401
        except Exception as e:
            return jsonify({'message': 'Error decoding token', 'error': str(e)}), 500

        return f(current_user, *args, **kwargs)

    return decorated

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        dob = request.form['dob']
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']

        if not username or not password:
            return jsonify({'message': 'Username and password are required'}), 400

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        user_data = {
            'name': name,
            'dob': dob,
            'email': email,
            'username': username,
            'password': hashed_password
        }

        try:
            users_collection.insert_one(user_data)
            return redirect('/login')
        except Exception as e:
            logging.error(f'Error registering user: {str(e)}')
            return jsonify({'message': 'Error registering user'}), 500

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = users_collection.find_one({'username': username})

        if not user or not check_password_hash(user['password'], password):
            return jsonify({'message': 'Invalid username or password'}), 401

        token = jwt.encode({'user_id': str(user['_id']), 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'])

        response = make_response(redirect('/display_task'))
        response.set_cookie('token', token, httponly=True)
        return response

    return render_template('login.html')

@app.route('/logout')
def logout():
    response = make_response(redirect('/login'))
    response.delete_cookie('token')
    return response

@app.route('/add_task', methods=['GET', 'POST'])
@token_required
def add_task_page(current_user):
    if request.method == 'POST':
        task_data = {
            'taskname': request.form['taskname'],
            'duration': int(request.form['duration']),
            'deadline': request.form['deadline'],
            'type_of_work': request.form['type_of_work'],
            'degree_of_importance': request.form['degree_of_importance'],
            'completion_status': 'Pending',
            'user_id': current_user['_id']  # Assign task to the current user
        }
        try:
            result = tasks_collection.insert_one(task_data)
            if result.inserted_id:
                return redirect('/display_task')  # Redirect to display tasks page
            else:
                return 'Error adding task'
        except Exception as e:
            logging.error(f'Error adding task: {str(e)}')
            return jsonify({'message': 'Error adding task'}), 500

    return render_template('add_tasks.html')

@app.route('/display_task', methods=['GET'])
@token_required
def display_tasks_page(current_user):
    try:
        tasks = list(tasks_collection.find({'user_id': current_user['_id']}))
        for task in tasks:
            task['_id'] = str(task['_id'])  # Convert ObjectId to string
        return render_template('display_tasks.html', tasks=tasks)
    except Exception as e:
        logging.error(f'Error fetching tasks: {str(e)}')
        return jsonify({'message': 'Error fetching tasks'}), 500

@app.route('/tasks', methods=['GET'])
@token_required
def get_tasks(current_user):
    try:
        tasks = list(mongo.db.tasks.find({"user_id": current_user['_id']}))
        serialized_tasks = json.dumps(tasks, default=str)  # Serialize ObjectId as string
        return jsonify(serialized_tasks)
    
    except Exception as e:
        logging.error(f'Error fetching tasks: {str(e)}')
        return jsonify({'message': 'Error fetching tasks'}), 500

@app.route('/tasks/<task_id>', methods=['PUT'])
@token_required
def update_task_status(current_user, task_id):
    try:
        request_data = request.get_json()
        new_status = request_data.get('completion_status')
        
        # Update task only if the task_id and current_user._id match
        result = tasks_collection.update_one({'_id': ObjectId(task_id), 'user_id': current_user['_id']}, {'$set': {'completion_status': new_status}})
        
        if result.modified_count > 0:
            return jsonify({'message': 'Task status updated successfully'})
        else:
            return jsonify({'message': 'Task not found or unauthorized'})
    
    except Exception as e:
        logging.error(f'Error updating task status: {str(e)}')
        return jsonify({'message': 'Error updating task status'}), 500

@app.route('/tasks/<task_id>', methods=['DELETE'])
@token_required
def delete_task(current_user, task_id):
    try:
        result = tasks_collection.delete_one({'_id': ObjectId(task_id), 'user_id': current_user['_id']})
        
        if result.deleted_count > 0:
            return jsonify({'message': 'Task deleted successfully'}), 200
        else:
            return jsonify({'message': 'Task not found'}), 404
    
    except Exception as e:
        logging.error(f'Error deleting task: {str(e)}')
        return jsonify({'message': 'Error deleting task'}), 500


if __name__ == '__main__':
    app.run(debug=True)
