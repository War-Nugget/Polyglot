import unittest
from flask import Flask, session
from app import create_app, db
from models.user import User
from werkzeug.security import generate_password_hash

class AuthTestCase(unittest.TestCase):
    def setUp(self):
        """Set up test variables and initialize app."""
        self.app = create_app('testing')
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()
            new_user = User(email='test@example.com', password=generate_password_hash('test1234'))
            db.session.add(new_user)
            db.session.commit()

    def tearDown(self):
        """Ensure that all data is cleared after tests."""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_user_signup(self):
        """Test API can register a user."""
        response = self.client.post('/auth/signup', data={'email': 'newuser@example.com', 'password': 'newuser123'})
        self.assertEqual(response.status_code, 201)

    def test_user_login(self):
        """Test API can log in a user."""
        response = self.client.post('/auth/login', data={'email': 'test@example.com', 'password': 'test1234'})
        self.assertEqual(response.status_code, 302)  # Redirect to dashboard
        
    def test_user_login_invalid(self):
        """Test API cannot log in a user with invalid credentials."""
        response = self.client.post('/auth/login', data={'email': 'test@example.com', 'password': 'test1234'})
        self.assertEqual(response.status_code, 401)

    def test_user_logout(self):
        """Test API can log out a user."""
        with self.client as c:
            c.post('/auth/login', data={'email': 'test@example.com', 'password': 'test1234'})
            response = c.get('/auth/logout')
            self.assertNotIn('user_id', session)
            self.assertEqual(response.status_code, 302)

    def test_user_dashboard(self):
        """Test API can access dashboard."""
        with self.client as c:
            c.post('/auth/login', data={'email': 'test@example.com', 'password': 'test1234'})
            response = c.get('/auth/dashboard')
            self.assertEqual(response.status_code, 200)
            self.assertIn('Welcome "user"', response.data.decode())
        
    def test_user_dashboard_unauthorized(self):
        """Test API cannot access dashboard without logging in."""
        response = self.client.get('/auth/dashboard')
        self.assertEqual(response.status_code, 302)
        
    
    
if __name__ == "__main__":
    unittest.main()
