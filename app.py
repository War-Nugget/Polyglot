from flask import Flask, jsonify, request, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

# Initialize Flask app
app = Flask(__name__)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///languageapp.db'
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db = SQLAlchemy(app)

# Define models
class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(128), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))

    def __init__(self, email, password):
        self.email = email
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.email}>'

# Create the database tables
@app._got_first_request
def create_tables():
    db.create_all()

# Routes
@app.route('/signup', methods=['POST'])
def signup():
    data = request.form
    email = data.get('email')
    password = data.get('password')
    if not email or not password:
        return jsonify({'message': 'Missing email or password'}), 400

    user = User.query.filter_by(email=email).first()
    if user:
        return jsonify({'message': 'Email already in use'}), 409

    new_user = User(email=email, password=password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User created successfully'}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.form
    user = User.query.filter_by(email=data.get('email')).first()
    if user and user.check_password(data.get('password')):
        session['user_id'] = user.id
        return redirect(url_for('dashboard'))
    return jsonify({'message': 'Invalid email or password'}), 401

@app.route('/dashboard')
def dashboard():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        return jsonify({'message': f'Welcome {user.email}'})
    return redirect(url_for('login'))

@app.route('/')
def index():
    return jsonify({'message': 'Welcome to the Language Learning App'})

# Run the Flask application
if __name__ == '__main__':
    app.run(debug=True)
