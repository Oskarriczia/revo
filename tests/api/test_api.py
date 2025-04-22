import sys
import os
import unittest
import requests
import json
from datetime import date, timedelta
import time
import string
import random

# Set base URL for API tests
BASE_URL = os.environ.get('API_URL', 'http://localhost:7777')

class HelloAppApiTestCase(unittest.TestCase):
    """API tests that hit the actual running service"""
    
    def generate_random_username(self, length=8):
        """Generate a random username with only letters"""
        return ''.join(random.choice(string.ascii_letters) for _ in range(length))
    
    def test_create_user_success(self):
        """Test successful user creation"""
        username = self.generate_random_username()
        payload = {"dateOfBirth": "1990-01-15"}
        
        response = requests.put(f"{BASE_URL}/hello/{username}", json=payload)
        self.assertEqual(response.status_code, 204)
        
        # Verify user was created by getting their details
        get_response = requests.get(f"{BASE_URL}/hello/{username}")
        self.assertEqual(get_response.status_code, 200)
        
    def test_update_existing_user(self):
        """Test updating an existing user"""
        username = self.generate_random_username()
        
        # Create user with initial birthday
        requests.put(f"{BASE_URL}/hello/{username}", json={"dateOfBirth": "1990-01-15"})
        
        # Update user with new birthday
        response = requests.put(f"{BASE_URL}/hello/{username}", json={"dateOfBirth": "1995-06-20"})
        self.assertEqual(response.status_code, 204)
        
        # Make a GET request and verify birthday calculation is correct
        today = date.today()
        next_birthday_month = 6
        next_birthday_day = 20
        
        # Calculate this year's birthday
        this_year_birthday = date(today.year, next_birthday_month, next_birthday_day)
        
        # If the birthday has already occurred this year, calculate for next year
        if this_year_birthday < today:
            this_year_birthday = date(today.year + 1, next_birthday_month, next_birthday_day)
        
        # Expected days until birthday
        expected_days = (this_year_birthday - today).days
        
        # Get the message and verify
        get_response = requests.get(f"{BASE_URL}/hello/{username}")
        self.assertEqual(get_response.status_code, 200)
        
        if expected_days == 0:
            self.assertIn("Happy birthday", get_response.json()["message"])
        else:
            self.assertIn(f"Your birthday is in {expected_days} day", get_response.json()["message"])
    
    def test_get_nonexistent_user(self):
        """Test getting a user that doesn't exist"""
        response = requests.get(f"{BASE_URL}/hello/nonexistentuserxyz123")
        self.assertEqual(response.status_code, 404)
        self.assertIn("not found", response.json()["error"])
    
    def test_username_validation(self):
        """Test username validation (letters only)"""
        test_cases = [
            ("user123", 400),  # Contains numbers
            ("user-name", 400),  # Contains dash
            ("user_name", 400),  # Contains underscore
            ("user.name", 400),  # Contains period
            ("validuser", 204)   # Valid username
        ]
        
        for username, expected_status in test_cases:
            response = requests.put(
                f"{BASE_URL}/hello/{username}", 
                json={"dateOfBirth": "1990-01-15"}
            )
            self.assertEqual(response.status_code, expected_status, f"Failed for username: {username}")
    
    def test_date_format_validation(self):
        """Test date format validation"""
        username = self.generate_random_username()
        test_cases = [
            ("1990-01-15", 204),     # Valid format
            ("15-01-1990", 400),     # Invalid format (DD-MM-YYYY)
            ("01/15/1990", 400),     # Invalid format (MM/DD/YYYY)
            ("1990.01.15", 400),     # Invalid format (YYYY.MM.DD)
            ("Jan 15, 1990", 400),   # Invalid format (text)
            ("15 Jan 1990", 400)     # Invalid format (text)
        ]
        
        for date_string, expected_status in test_cases:
            response = requests.put(
                f"{BASE_URL}/hello/{username}",
                json={"dateOfBirth": date_string}
            )
            self.assertEqual(response.status_code, expected_status, f"Failed for date: {date_string}")
    
    def test_future_date_validation(self):
        """Test validation for future dates"""
        username = self.generate_random_username()
        future_date = (date.today() + timedelta(days=1)).strftime('%Y-%m-%d')
        
        response = requests.put(
            f"{BASE_URL}/hello/{username}",
            json={"dateOfBirth": future_date}
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("Date of birth must be before today", response.json()["error"])
    
    def test_missing_date_of_birth(self):
        """Test validation for missing dateOfBirth"""
        username = self.generate_random_username()
        
        response = requests.put(
            f"{BASE_URL}/hello/{username}",
            json={}  # Empty JSON
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("Date of birth is required", response.json()["error"])
    
    def test_birthday_today(self):
        """Test birthday message when birthday is today"""
        username = self.generate_random_username()
        today = date.today()
        birthday = date(1990, today.month, today.day).strftime('%Y-%m-%d')
        
        # Create user with birthday today
        requests.put(f"{BASE_URL}/hello/{username}", json={"dateOfBirth": birthday})
        
        # Get birthday message
        response = requests.get(f"{BASE_URL}/hello/{username}")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Happy birthday", response.json()["message"])
    
    def test_very_long_username(self):
        """Test with very long username that still contains only letters"""
        username = "a" * 100  # 100 character username
        
        response = requests.put(
            f"{BASE_URL}/hello/{username}",
            json={"dateOfBirth": "1990-01-15"}
        )
        
        # The API should handle long usernames (PostgreSQL VARCHAR(50) might truncate)
        # We just verify that the request doesn't fail with a server error
        # Currently this fails on purpouse, just to prove that the CI process works :)
        self.assertNotEqual(response.status_code, 500)
    
    def test_empty_username(self):
        """Test with empty username"""
        response = requests.put(
            f"{BASE_URL}/hello/",  # Empty username
            json={"dateOfBirth": "1990-01-15"}
        )
        
        # This should return a 404 as the route won't match
        self.assertEqual(response.status_code, 404)

if __name__ == '__main__':
    unittest.main()