from flask import Flask, request, redirect, url_for, session, render_template_string, jsonify
import os
import json
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'

USERS_FILE = 'users.json'
LESSONS_FILE = 'lessons.json'

def load_data(file):
    if os.path.exists(file):
        with open(file, 'r') as f:
            return json.load(f)
    return []

def save_data(file, data):
    with open(file, 'w') as f:
        json.dump(data, f, indent=4)

@app.route('/')
def index():
    user = session.get('user')
    now = datetime.now()
    date_str = now.strftime('%A, %B %d, %Y %H:%M')
    if not user:
        return redirect('/login')
    return render_template_string("""
        <html>
        <head>
            <title>Dashboard</title>
            <style>
                body {
                    font-family: 'Arial', sans-serif;
                    background-color: #f0f0f0;
                    color: #333;
                    margin: 0;
                    padding: 0;
                }
                header {
                    background-color: #003366;
                    color: #ffffff;
                    padding: 20px 0;
                    text-align: center;
                }
                header h1 {
                    font-size: 2.5em;
                    margin: 0;
                }
                nav {
                    background-color: #004d99;
                    padding: 10px 0;
                    text-align: center;
                }
                nav a {
                    color: #ff6600;
                    text-decoration: none;
                    padding: 12px 25px;
                    margin: 0 10px;
                    font-size: 1.1em;
                }
                nav a:hover {
                    background-color: #ff6600;
                    color: #003366;
                    border-radius: 5px;
                }
                main {
                    padding: 40px 20px;
                    max-width: 1200px;
                    margin: auto;
                    background-color: #ffffff;
                    border-radius: 10px;
                    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                }
                form {
                    background-color: #f9f9f9;
                    border-radius: 8px;
                    padding: 20px;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                    max-width: 400px;
                    margin: 0 auto;
                }
                form input {
                    width: 100%;
                    padding: 12px;
                    margin: 10px 0;
                    border: 1px solid #ddd;
                    border-radius: 5px;
                    font-size: 1em;
                }
                form button {
                    width: 100%;
                    padding: 12px;
                    background-color: #003366;
                    color: #fff;
                    border: none;
                    border-radius: 5px;
                    font-size: 1.1em;
                    cursor: pointer;
                }
                form button:hover {
                    background-color: #004d99;
                }
                a {
                    color: #003366;
                    text-decoration: none;
                }
                a:hover {
                    color: #ff6600;
                }
                ul {
                    list-style-type: none;
                    padding: 0;
                }
                ul li {
                    background-color: #f9f9f9;
                    padding: 15px;
                    margin: 10px 0;
                    border-radius: 8px;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
                }
                ul li a {
                    color: #003366;
                    text-decoration: none;
                    margin-right: 20px;
                    font-weight: bold;
                }
                ul li form {
                    display: inline;
                    margin: 0;
                }
                table {
                    width: 100%;
                    border-collapse: collapse;
                }
                table th, table td {
                    padding: 12px;
                    border: 1px solid #ddd;
                    text-align: center;
                }
                table th {
                    background-color: #003366;
                    color: #ffffff;
                }
                table tr:nth-child(even) {
                    background-color: #f2f2f2;
                }
                table tr:hover {
                    background-color: #ff6600;
                    color: #fff;
                }
                hr {
                    border: 1px solid #ddd;
                    margin: 40px 0;
                }
            </style>
        </head>
        <body>
            <header>
                <h1>Educational Platform</h1>
                <p>{{date}}</p>
                <nav>
                    <a href="/">Home</a>
                    <a href="/profile">Profile</a>
                    {% if user.email == 'admin@example.com' %}
                        <a href="/admin">Admin</a>
                    {% endif %}
                    <a href="/logout">Logout</a>
                </nav>
            </header>
            <main>
                <h2>Welcome, {{user.name}}</h2>
            </main>
        </body>
        </html>
    """, user=user, date=date_str)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        users = load_data(USERS_FILE)
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        if any(u['email'] == email for u in users):
            return "User already exists"
        users.append({'name': name, 'email': email, 'password': password, 'profile_image': ''})
        save_data(USERS_FILE, users)
        return redirect('/login')
    return render_template_string("""
        <html><head><title>Register</title><style>{{style}}</style></head>
        <body><header><h1>Register</h1></header>
        <main>
        <form method="POST">
            <input name="name" placeholder="Full Name" required>
            <input name="email" type="email" placeholder="Email" required>
            <input name="password" type="password" placeholder="Password" required>
            <button type="submit">Register</button>
        </form>
        <p><a href="/login">Already have an account? Login</a></p>
        </main></body></html>
    """, style=css_style)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        users = load_data(USERS_FILE)
        for user in users:
            if user['email'] == email and user['password'] == password:
                session['user'] = user
                return redirect('/')
        return "Invalid credentials"
    return render_template_string("""
        <html><head><title>Login</title><style>{{style}}</style></head>
        <body><header><h1>Login</h1></header>
        <main>
        <form method="POST">
            <input name="email" type="email" placeholder="Email" required>
            <input name="password" type="password" placeholder="Password" required>
            <button type="submit">Login</button>
        </form>
        <p><a href="/register">Create Account</a></p>
        </main></body></html>
    """, style=css_style)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/login')

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user' not in session:
        return redirect('/login')
    user = session['user']
    if request.method == 'POST':
        user['name'] = request.form['name']
        user['password'] = request.form['password']
        users = load_data(USERS_FILE)
        for u in users:
            if u['email'] == user['email']:
                u.update(user)
        save_data(USERS_FILE, users)
        session['user'] = user
        return redirect('/profile')
    return render_template_string("""
        <html><head><title>Profile</title><style>{{style}}</style></head>
        <body><header><h1>Profile Settings</h1></header>
        <main>
        <form method="POST">
            <input name="name" value="{{ user.name }}" required>
            <input name="password" type="password" value="{{ user.password }}" required>
            <button type="submit">Update Profile</button>
        </form>
        </main></body></html>
    """, user=user, style=css_style)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    user = session.get('user')
    if not user or user['email'] != 'admin@example.com':
        return "Access Denied"
    users = load_data(USERS_FILE)
    lessons = load_data(LESSONS_FILE)
    return render_template_string("""
        <html><head><title>Admin</title><style>{{style}}</style></head>
        <body><header><h1>Admin Panel</h1></header>
        <main>
        <h2>Users</h2>
        <ul>
        {% for u in users %}
            <li>{{ u.name }} - {{ u.email }}
                <form action="/admin/delete_user/{{ u.email }}" method="POST" style="display:inline;">
                    <button>Delete</button>
                </form>
            </li>
        {% endfor %}
        </ul>
        <h2>Add Lesson</h2>
        <form method="POST" action="/admin/add_lesson">
            <input name="title" placeholder="Lesson Title" required>
            <input name="content" placeholder="Lesson Content" required>
            <button type="submit">Add</button>
        </form>
        <h2>Lessons</h2>
        <ul>
        {% for l in lessons %}
            <li><b>{{l.title}}</b>: {{l.content}}</li>
        {% endfor %}
        </ul>
        </main></body></html>
    """, users=users, lessons=lessons, style=css_style)

@app.route('/admin/add_lesson', methods=['POST'])
def add_lesson():
    if 'user' not in session or session['user']['email'] != 'admin@example.com':
        return "Access Denied"
    lessons = load_data(LESSONS_FILE)
    lessons.append({
        'title': request.form['title'],
        'content': request.form['content']
    })
    save_data(LESSONS_FILE, lessons)
    return redirect('/admin')

@app.route('/admin/delete_user/<email>', methods=['POST'])
def delete_user(email):
    if 'user' not in session or session['user']['email'] != 'admin@example.com':
        return "Access Denied"
    users = load_data(USERS_FILE)
    users = [u for u in users if u['email'] != email]
    save_data(USERS_FILE, users)
    return redirect('/admin')

# ==== Run app ====
if __name__ == '__main__':
    app.run(debug=True)
