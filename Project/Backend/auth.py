from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, User
from paths import DATA_DIR, DB_PATH

auth_bp = Blueprint('auth', __name__)
DATA_DIR.mkdir(parents=True, exist_ok=True)
engine = create_engine(f"sqlite:///{DB_PATH.as_posix()}")
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(bind=engine)
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

class UserModel(UserMixin):
    def __init__(self, user_obj):
        self.id = user_obj.id
        self.username = user_obj.username
        self._db_obj = user_obj

    def check_password(self, password):
        return check_password_hash(self._db_obj.password_hash, password)

@login_manager.user_loader
def load_user(user_id):
    session = SessionLocal()
    user = session.query(User).filter(User.id == int(user_id)).first()
    session.close()
    if user:
        return UserModel(user)
    return None

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        repeat_password = request.form.get('repeat_password', '')
        
        if not username or not password or not repeat_password:
            flash('All fields are required')
            return redirect(url_for('auth.register'))
        
        if password != repeat_password:
            flash('Passwords do not match')
            return redirect(url_for('auth.register'))
        
        session = SessionLocal()
        if session.query(User).filter(User.username == username).first():
            flash('Username already taken')
            session.close()
            return redirect(url_for('auth.register'))
        user = User(username=username, password_hash=generate_password_hash(password))
        session.add(user)
        session.commit()
        session.close()
        flash('Registration successful; please log in.')
        return redirect(url_for('auth.login'))
    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        session = SessionLocal()
        user = session.query(User).filter(User.username == username).first()
        session.close()
        if user and check_password_hash(user.password_hash, password):
            login_user(UserModel(user))
            return redirect(url_for('index'))
        flash('Invalid credentials')
    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))
