import unittest

import sys
import os
import json
import psycopg2

from datetime import datetime, date, timedelta

# Add src directory to path to import main
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.main import app, connection_pool

class HelloAppTestCase(unittest.TestCase):
    def setUp(self):
        # Configure the app for testing
        app.config['TESTING'] = True
        self.client = app.test_client()
        
        # Clear test data before each test
        conn = connection_pool.getconn()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users")
            conn.commit()
            cursor.close()
        finally:
            connection_pool.putconn(conn)
    
    def test_update_user_valid(self):
        """Test updating a user with valid data"""
        response = self.client.put(
            '/hello/john',
            data=json.dumps({'dateOfBirth': '1990-01-15'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 204)
        
        # Verify data was stored correctly
        conn = connection_pool.getconn()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT date_of_birth FROM users WHERE username = %s", ('john',))
            result = cursor.fetchone()
            cursor.close()
            
            self.assertIsNotNone(result)
            self.assertEqual(result[0].strftime('%Y-%m-%d'), '1990-01-15')
        finally:
            connection_pool.putconn(conn)
    
    def test_update_user_invalid_username(self):
        """Test updating a user with invalid username"""
        response = self.client.put(
            '/hello/john123',  # contains numbers
            data=json.dumps({'dateOfBirth': '1990-01-15'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('Username must contain only letters', response.get_json()['error'])
    
    def test_update_user_invalid_date_format(self):
        """Test updating a user with invalid date format"""
        response = self.client.put(
            '/hello/john',
            data=json.dumps({'dateOfBirth': '15-01-1990'}),  # wrong format
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('Invalid date format', response.get_json()['error'])
    
    def test_update_user_future_date(self):
        """Test updating a user with future date"""
        future_date = (date.today() + timedelta(days=10)).strftime('%Y-%m-%d')
        response = self.client.put(
            '/hello/john',
            data=json.dumps({'dateOfBirth': future_date}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('Date of birth must be before today', response.get_json()['error'])

    def test_update_user_birthday_today_this_year(self):
        """Test updating a user with future date"""
        today = date.today().strftime('%Y-%m-%d')
        response = self.client.put(
            '/hello/johnyMnemonic',
            data=json.dumps({'dateOfBirth': today}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('You sure learned computers fast!', response.get_json()['error'])

    def test_get_user_not_found(self):
        """Test getting a non-existent user"""
        response = self.client.get('/hello/nonex1stent')
        self.assertEqual(response.status_code, 404)
        self.assertIn('not found', response.get_json()['error'])
    
    def test_get_user_birthday_today(self):
        """Test getting user whose birthday is today"""
        # Create a user with birthday today
        today = date.today()
        # but old, not a newborn ;-)
        birthday = date(1990, today.month, today.day).strftime('%Y-%m-%d')
        
        # Add user
        self.client.put(
            '/hello/birthdayuser',
            data=json.dumps({'dateOfBirth': birthday}),
            content_type='application/json'
        )
        
        # Get birthday message
        response = self.client.get('/hello/birthdayuser')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Happy birthday', response.get_json()['message'])
    
    def test_get_user_birthday_future(self):
        """Test getting user whose birthday is in the future"""
        # Calculate a date that's a few days from now in the same year
        today = date.today()
        future_day = min(today.day + 5, 28)  # Avoid month end issues
        future_month = today.month
        
        # If we're crossing to next month
        if future_day < today.day:
            future_month = (today.month % 12) + 1
        
        birthday = date(1990, future_month, future_day).strftime('%Y-%m-%d')
        
        # Add user
        self.client.put(
            '/hello/futureuser',
            data=json.dumps({'dateOfBirth': birthday}),
            content_type='application/json'
        )
        
        # Get birthday message
        response = self.client.get('/hello/futureuser')
        self.assertEqual(response.status_code, 200)
        message = response.get_json()['message']
        self.assertIn('Your birthday is in', message)
        
        # Extract days and verify it's a positive number
        import re
        days = int(re.search(r'in (\d+) day', message).group(1))
        self.assertGreater(days, 0)

if __name__ == '__main__':
    unittest.main()