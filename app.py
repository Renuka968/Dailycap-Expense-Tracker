import os
from datetime import datetime, date
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_mail import Mail, Message
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///expense.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Mail settings (optional)
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', '587'))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True') == 'True'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME', '')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD', '')
app.config['SENDER_EMAIL'] = os.getenv('SENDER_EMAIL', '')

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
mail = Mail(app)

# ----------------- Models -----------------
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    daily_limit = db.Column(db.Integer, default=500)

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    amount = db.Column(db.Integer, nullable=False)
    category = db.Column(db.String(64), nullable=False)
    note = db.Column(db.String(256))
    created_at = db.Column(db.Date, default=date.today)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ----------------- Helpers -----------------
def send_alert_email(to_email, subject, body):
    if not app.config['MAIL_USERNAME'] or not app.config['MAIL_PASSWORD']:
        return False
    try:
        msg = Message(subject=subject, recipients=[to_email], body=body, sender=app.config['SENDER_EMAIL'])
        mail.send(msg)
        return True
    except Exception:
        return False

def get_today_total(user_id):
    today = date.today()
    total = db.session.query(db.func.sum(Expense.amount)).filter_by(user_id=user_id, created_at=today).scalar()
    return total or 0

# ----------------- Routes -----------------
@app.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name'].strip()
        email = request.form['email'].strip().lower()
        password = request.form['password']
        if User.query.filter_by(email=email).first():
            flash('Email already exists.', 'error')
            return redirect(url_for('signup'))
        u = User(name=name, email=email, password=password, daily_limit=500)
        db.session.add(u)
        db.session.commit()
        flash('Account created. Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form['email'].strip().lower()
        password = request.form['password']
        u = User.query.filter_by(email=email, password=password).first()
        if not u:
            flash('Invalid credentials', 'error')
            return redirect(url_for('login'))
        login_user(u)
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out.','info')
    return redirect(url_for('home'))

@app.route('/dashboard')
@login_required
def dashboard():
    today_total = get_today_total(current_user.id)
    limit = current_user.daily_limit or 0
    alert = None
    if limit and today_total >= limit:
        alert = f'You have exceeded your daily budget of ₹{limit}! (Spent ₹{today_total})'
    elif limit and today_total >= 0.9 * limit:
        alert = f'You are nearing your daily limit. Spent ₹{today_total} / ₹{limit}.'
    # recent txns
    txns = Expense.query.filter_by(user_id=current_user.id).order_by(Expense.id.desc()).limit(10).all()
    return render_template('dashboard.html', today_total=today_total, limit=limit, alert=alert, txns=txns)

@app.route('/expense/add', methods=['POST'])
@login_required
def add_expense():
    amount = int(request.form['amount'])
    category = request.form['category']
    note = request.form.get('note', '')
    e = Expense(user_id=current_user.id, amount=amount, category=category, note=note, created_at=date.today())
    db.session.add(e)
    db.session.commit()

    # Check alert and optionally email
    total = get_today_total(current_user.id)
    limit = current_user.daily_limit or 0
    if limit and (total >= limit or total >= 0.9 * limit):
        status = "Exceeded" if total >= limit else "Nearing"
        subject = f"[DailyCap] {status} your daily budget"
        body = f"Hi {current_user.name},\n\nYou've spent ₹{total} of your daily budget ₹{limit} today.\n\n— DailyCap"
        send_alert_email(current_user.email, subject, body)

    return redirect(url_for('dashboard'))

@app.route('/budget', methods=['POST'])
@login_required
def set_budget():
    daily_limit = int(request.form['daily_limit'])
    current_user.daily_limit = daily_limit
    db.session.commit()
    flash('Budget updated.', 'success')
    return redirect(url_for('dashboard'))

# CLI helper to init DB
@app.cli.command('init-db')
def init_db():
    db.create_all()
    print('Database initialized.')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
