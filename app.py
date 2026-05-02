import os
from dotenv import load_dotenv
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_dance.contrib.google import make_google_blueprint, google
from models import db, User, Application

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'fallback-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///applytrack.db'
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

db.init_app(app)

google_bp = make_google_blueprint(
    client_id=os.getenv('GOOGLE_CLIENT_ID'),
    client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
    redirect_to='google_login_callback',
    scope=['openid', 'https://www.googleapis.com/auth/userinfo.email',
           'https://www.googleapis.com/auth/userinfo.profile']
)
app.register_blueprint(google_bp, url_prefix='/login')

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ── LANDING PAGE ──
@app.route('/')
def landing():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('landing.html')

# ── DASHBOARD ──
@app.route('/dashboard')
@login_required
def dashboard():
    apps = Application.query.filter_by(user_id=current_user.id).order_by(Application.id.desc()).all()
    total = len(apps)
    interviews = len([a for a in apps if a.status == 'Interview'])
    offers = len([a for a in apps if a.status == 'Offer'])
    rejected = len([a for a in apps if a.status == 'Rejected'])
    return render_template('index.html', applications=apps, total=total,
                           interviews=interviews, offers=offers, rejected=rejected)

# ── ADD ──
@app.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    if request.method == 'POST':
        new_app = Application(
            company=request.form['company'],
            role=request.form['role'],
            date=request.form['date'],
            status=request.form['status'],
            notes=request.form['notes'],
            user_id=current_user.id
        )
        db.session.add(new_app)
        db.session.commit()
        flash('Application added!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('add.html')

# ── EDIT ──
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    app_entry = Application.query.get_or_404(id)
    if request.method == 'POST':
        app_entry.company = request.form['company']
        app_entry.role = request.form['role']
        app_entry.date = request.form['date']
        app_entry.status = request.form['status']
        app_entry.notes = request.form['notes']
        db.session.commit()
        flash('Application updated!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('edit.html', app=app_entry)

# ── DELETE ──
@app.route('/delete/<int:id>')
@login_required
def delete(id):
    app_entry = Application.query.get_or_404(id)
    db.session.delete(app_entry)
    db.session.commit()
    flash('Application deleted!', 'success')
    return redirect(url_for('dashboard'))

# ── LOGIN ──
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and check_password_hash(user.password, request.form['password']):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Invalid username or password', 'danger')
    return render_template('login.html')

# ── GOOGLE CALLBACK ──
@app.route('/login/google/callback/done')
def google_login_callback():
    if not google.authorized:
        flash('Google login failed.', 'danger')
        return redirect(url_for('login'))

    resp = google.get('/oauth2/v2/userinfo')
    if not resp.ok:
        flash('Failed to fetch Google account info.', 'danger')
        return redirect(url_for('login'))

    info = resp.json()
    google_email = info['email']
    google_name = info.get('name', google_email.split('@')[0]).replace(' ', '_')

    # Find or create user
    user = User.query.filter_by(username=google_email).first()
    if not user:
        user = User(
            username=google_email,
            password=generate_password_hash(os.urandom(16).hex())
        )
        db.session.add(user)
        db.session.commit()

    login_user(user)
    flash(f'Welcome, {google_name}! 🎉', 'success')
    return redirect(url_for('dashboard'))

# ── REGISTER ──
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        existing = User.query.filter_by(username=request.form['username']).first()
        if existing:
            flash('Username already exists', 'danger')
            return redirect(url_for('register'))
        new_user = User(
            username=request.form['username'],
            password=generate_password_hash(request.form['password'])
        )
        db.session.add(new_user)
        db.session.commit()
        flash('Account created! Please login.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

# ── LOGOUT ──
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)