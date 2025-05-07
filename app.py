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
            <style>{{style}}</style>
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
    """, user=user, date=date_str, style=css_style)

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
    return render_template_string(register_template, style=css_style)

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
    return render_template_string(login_template, style=css_style)

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
    return render_template_string(profile_template, user=user, style=css_style)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    user = session.get('user')
    if not user or user['email'] != 'admin@example.com':
        return "Access Denied"
    users = load_data(USERS_FILE)
    lessons = load_data(LESSONS_FILE)
    return render_template_string(admin_template, users=users, lessons=lessons, style=css_style)

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

# ==== Templates (as Python strings) ====

css_style = """
body { font-family: sans-serif; background: #f4f4f4; color: #333; }
header { background: #003366; color: white; padding: 20px; }
nav a { margin: 10px; color: orange; text-decoration: none; }
main { padding: 20px; }
form input, form button { margin: 10px 0; padding: 10px; width: 100%; }
form { max-width: 400px; margin: auto; background: white; padding: 20px; border-radius: 10px; }
"""

register_template = """
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
"""

login_template = """
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
"""

profile_template = """
<html><head><title>Profile</title><style>{{style}}</style></head>
<body><header><h1>Profile Settings</h1></header>
<main>
<form method="POST">
    <input name="name" value="{{ user.name }}" required>
    <input name="password" type="password" value="{{ user.password }}" required>
    <button type="submit">Update Profile</button>
</form>
</main></body></html>
"""

admin_template = """
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
"""

# ==== Run app ====
if __name__ == '__main__':
    app.run(debug=True)
