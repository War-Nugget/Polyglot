from flask import Flask, jsonify, request, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import unittest

# Initialize Flask app and database
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///languageapp.db'
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['TESTING'] = True

db = SQLAlchemy(app)

# Define models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(128), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))

    def __init__(self, email, password):
        self.email = email
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Language(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

class Topic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    language_id = db.Column(db.Integer, db.ForeignKey('language.id'))
    language = db.relationship('Language', backref=db.backref('topics', lazy=True))

class Progress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    topic_id = db.Column(db.Integer, db.ForeignKey('topic.id'))
    completed = db.Column(db.Boolean, default=False)
    user = db.relationship('User', backref='progress')
    topic = db.relationship('Topic', backref='progress')

# Routes for user management
@app.route('/signup', methods=['POST'])
def signup():
    data = request.form
    user = User.query.filter_by(email=data.get('email')).first()
    if user:
        return jsonify({'message': 'Email already registered'}), 409
    new_user = User(email=data.get('email'), password=data.get('password'))
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User created successfully'}), 201

@app.route('/login', methods=['POST'])
def login():
    user = User.query.filter_by(email=request.form.get('email')).first()
    if user and user.check_password(request.form.get('password')):
        session['user_id'] = user.id
        return jsonify({'message': 'Logged in successfully'}), 200
    return jsonify({'message': 'Invalid email or password'}), 401

@app.route('/progress/update', methods=['POST'])
def update_progress():
    if 'user_id' not in session:
        return jsonify({'message': 'User not authenticated'}), 403
    topic_id = request.form.get('topic_id')
    completed = request.form.get('completed', type=bool)
    progress = Progress.query.filter_by(user_id=session['user_id'], topic_id=topic_id).first()
    if not progress:
        progress = Progress(user_id=session['user_id'], topic_id=topic_id, completed=completed)
    else:
        progress.completed = completed
    db.session.add(progress)
    db.session.commit()
    return jsonify({'message': 'Progress updated successfully'}), 200

@app.route('/offline/topics/<int:language_id>')
def offline_topics(language_id):
    topics = Topic.query.filter_by(language_id=language_id).all()
    return jsonify([{'id': topic.id, 'name': topic.name} for topic in topics])

# Testing
class AppTestCase(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        with app.app_context():
            db.create_all()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_signup_login(self):
        # Test signing up a user
        response = self.client.post('/signup', data={'email': 'test@example.com', 'password': 'test1234'})
        self.assertEqual(response.status_code, 201)
        # Test logging in the same user
        response = self.client.post('/login', data={'email': 'test@example.com', 'password': 'test1234'})
        self.assertEqual(response.status_code, 200)

    def test_progress_update(self):
        # Setup a user and a topic
        self.client.post('/signup', data={'email': 'progress@example.com', 'password': 'password'})
        self.client.post('/login', data={'email' : 'progress@example.com', 'password': 'password'})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    unittest.main()
