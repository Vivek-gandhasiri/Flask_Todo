**TODO Application**
A simple TODO application built using Flask and MongoDB, with JWT authentication.

** Table of Contents**
Introduction
Features
Installation
Usage

**Introduction**
This TODO application allows users to manage their tasks efficiently. Users can register/login, add tasks with details such as duration, deadline, type of work, and degree of importance. They can mark tasks as completed, partially completed, or pending. Tasks can also be updated and deleted. Authentication is handled using JWT (JSON Web Tokens) for secure user sessions.

**Features**
User registration and login with JWT authentication
Add new tasks with details
View list of tasks with completion status
Update task status
Delete tasks
**
Installation**

Prerequisites

Before you begin, ensure you have the following installed:

Python 3
MongoDB
Flask
Installation Steps
Clone the repository:

bash
Copy code
git clone https://github.com/yourusername/todo-application.git
cd todo-application
Install dependencies:

bash
Copy code
pip install -r requirements.txt
Start MongoDB service.

Run the application:

bash
Copy code
python app.py
Usage
Registration and Login
Open your web browser and go to http://localhost:5000/register.
Fill out the registration form with your details and submit.
After successful registration, you will be redirected to the login page.
Log in with your username and password.
Adding a Task
After logging in, click on "Add Task" in the navigation menu or go to http://localhost:5000/add_task.
Fill out the task details (Task Name, Duration, Deadline, Type of Work, Degree of Importance).
Submit the form to add the task.
Viewing Tasks
After adding tasks, click on "Display Tasks" in the navigation menu or go to http://localhost:5000/display_task.
You will see a list of tasks with details.
Tasks are color-coded based on their completion status (Completed, Partially Completed, Pending).
Updating Task Status
On the "Display Tasks" page, select a task from the list.
Change the status using the dropdown menu (Pending, Partially Completed, Completed).
The task list will update automatically.
Deleting a Task
On the "Display Tasks" page, each task has a delete button.
Click on the delete button to remove the task from the list.
Confirm the deletion when prompted.