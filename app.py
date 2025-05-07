from flask import Flask, render_template, request, redirect, url_for, jsonify, session
import json
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# مسار لتخزين البيانات
USERS_FILE = 'users.json'
LESSONS_FILE = 'lessons.json'

# تحميل البيانات من ملف JSON
def load_data(file_name):
    if os.path.exists(file_name):
        with open(file_name, 'r') as file:
            return json.load(file)
    return []

# حفظ البيانات إلى ملف JSON
def save_data(file_name, data):
    with open(file_name, 'w') as file:
        json.dump(data, file, indent=4)

# الصفحة الرئيسية
@app.route('/')
def index():
    if 'user' in session:
        return render_template('index.html', user=session['user'])
    return redirect(url_for('login'))

# صفحة التسجيل
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        users = load_data(USERS_FILE)
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        # التحقق من وجود المستخدم
        for user in users:
            if user['email'] == email:
                return 'User already exists'

        # إضافة المستخدم الجديد
        users.append({'name': name, 'email': email, 'password': password, 'profile_image': ''})
        save_data(USERS_FILE, users)
        return redirect(url_for('login'))

    return render_template('register.html')

# صفحة تسجيل الدخول
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        users = load_data(USERS_FILE)
        for user in users:
            if user['email'] == email and user['password'] == password:
                session['user'] = user
                return redirect(url_for('index'))

        return 'Invalid credentials'

    return render_template('login.html')

# صفحة البروفايل
@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user' not in session:
        return redirect(url_for('login'))

    user = session['user']

    if request.method == 'POST':
        user['name'] = request.form['name']
        user['password'] = request.form['password']
        if 'profile_image' in request.files:
            image = request.files['profile_image']
            if image.filename.endswith(('.jpg', '.png', '.jpeg')):
                image_path = os.path.join('static/images', image.filename)
                image.save(image_path)
                user['profile_image'] = image_path

        # تحديث بيانات المستخدم
        users = load_data(USERS_FILE)
        for i, u in enumerate(users):
            if u['email'] == user['email']:
                users[i] = user
        save_data(USERS_FILE, users)

        session['user'] = user  # تحديث البيانات في الجلسة
        return redirect(url_for('profile'))

    return render_template('profile.html', user=user)

# عرض الدروس
@app.route('/lessons', methods=['GET'])
def lessons():
    lessons = load_data(LESSONS_FILE)
    return jsonify(lessons)

# إضافة درس جديد (لوحة الأدمن)
@app.route('/admin/add_lesson', methods=['POST'])
def add_lesson():
    if 'user' not in session or session['user']['email'] != 'admin@example.com':
        return 'Access Denied', 403

    title = request.form['title']
    content = request.form['content']
    lessons = load_data(LESSONS_FILE)

    lesson = {'title': title, 'content': content}
    lessons.append(lesson)
    save_data(LESSONS_FILE, lessons)

    return redirect(url_for('admin'))

# صفحة لوحة الأدمن
@app.route('/admin')
def admin():
    if 'user' not in session or session['user']['email'] != 'admin@example.com':
        return 'Access Denied', 403

    users = load_data(USERS_FILE)
    lessons = load_data(LESSONS_FILE)

    return render_template('admin.html', users=users, lessons=lessons)

# حذف مستخدم (لوحة الأدمن)
@app.route('/admin/delete_user/<email>', methods=['POST'])
def delete_user(email):
    if 'user' not in session or session['user']['email'] != 'admin@example.com':
        return 'Access Denied', 403

    users = load_data(USERS_FILE)
    users = [user for user in users if user['email'] != email]
    save_data(USERS_FILE, users)

    return redirect(url_for('admin'))

# حظر مستخدم (لوحة الأدمن)
@app.route('/admin/block_user/<email>', methods=['POST'])
def block_user(email):
    if 'user' not in session or session['user']['email'] != 'admin@example.com':
        return 'Access Denied', 403

    users = load_data(USERS_FILE)
    for user in users:
        if user['email'] == email:
            user['blocked'] = True
    save_data(USERS_FILE, users)

    return redirect(url_for('admin'))

# تسجيل الخروج
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
