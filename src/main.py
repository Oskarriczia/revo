import os
import re
import traceback
import sys
import psycopg2
import logging

from datetime import datetime, date
from flask import Flask, request, jsonify

from psycopg2 import pool
from psycopg2.extras import RealDictCursor

app = Flask(__name__)

# config
PORT = int(os.environ.get('PORT', 7777))
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_NAME = os.environ.get('DB_NAME', 'hello_app')
DB_USER = os.environ.get('DB_USER', 'postgres')
DB_PASS = os.environ.get('DB_PASS', 'postgres')
DB_PORT = os.environ.get('DB_PORT', '5432')

# Create a connection pool
# This is not strictly required, but it's a good practice to reuse connections, instead of creating new ones every request
connection_pool = pool.ThreadedConnectionPool(
    minconn=1,
    maxconn=5,
    host=DB_HOST,
    database=DB_NAME,
    user=DB_USER,
    password=DB_PASS,
    port=DB_PORT
)

# Create table if it doesn't exist
def init_db():
    conn = connection_pool.getconn()
    try:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                username VARCHAR(50) PRIMARY KEY,
                date_of_birth DATE NOT NULL
            )
        ''')
        conn.commit()
        cursor.close()
    finally:
        connection_pool.putconn(conn)

init_db()

def calculate_days_until_birthday(dob):
    today = date.today()
    
    birthday = date(today.year, dob.month, dob.day)
    
    # If the birthday has already occurred this year, calculate for next year
    if birthday < today:
        birthday = date(today.year + 1, dob.month, dob.day)
    
    days_until_birthday = (birthday - today).days
    
    return days_until_birthday

### ROUTES

@app.route('/hello/<username>', methods=['PUT'])
def update_user(username):
    # fail fast
    if not re.match(r'^[a-zA-Z]+$', username):
        return jsonify({"error": "Username must contain only letters"}), 400
    
    # Parse and validate the request body
    data = request.get_json()
    
    if not data or 'dateOfBirth' not in data:
        return jsonify({"error": "Date of birth is required"}), 400
    
    try:
        date_of_birth = datetime.strptime(data['dateOfBirth'], '%Y-%m-%d').date()
    except ValueError:
        return jsonify({"error": "Invalid date format. Please use one of the best date formats - YYYY-MM-DD"}), 400
    
    # Validate date (must be before today)
    today = date.today()

    if date_of_birth == today:
        return jsonify({"error": f"Happy birthday {username}! You sure learned computers fast!"}), 400

    if date_of_birth > today:
        return jsonify({"error": "Date of birth must be before today"}), 400
    
    # Save/update user in the database
    conn = connection_pool.getconn()
    try:
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO users (username, date_of_birth) VALUES (%s, %s) "
            "ON CONFLICT (username) DO UPDATE SET date_of_birth = EXCLUDED.date_of_birth",
            (username, date_of_birth)
        )

        conn.commit()
        cursor.close()
    except Exception as e: #any exception
        logging.error(e)
        return jsonify({"error": "Error saving data"}), 500
    finally:
        cursor.close()
        connection_pool.putconn(conn)
    
    return "", 204

@app.route('/hello/<username>', methods=['GET'])
def get_hello_message(username):
    conn = connection_pool.getconn()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute("SELECT date_of_birth FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()

        cursor.close()

        if not user:
            return jsonify({"error": f"User '{username}' not found"}), 404
        
        # Calculate days until birthday
        dob = user['date_of_birth']
        days_until_birthday = calculate_days_until_birthday(dob)
        
        # Prepare the message
        if days_until_birthday == 0:
            message = f"Hello, {username}! Happy birthday!"
        else:
            message = f"Hello, {username}! Your birthday is in {days_until_birthday} day(s)"
        
        return jsonify({"message": message}), 200

    except Exception as e: #any exception
        logging.error(e)
        return jsonify({"error": f"User '{username}' not found"}), 404
    finally:
        cursor.close()
        connection_pool.putconn(conn)

# healthcheck endpoint
@app.route('/health', methods=['GET'])
def get_health():
    conn = connection_pool.getconn()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute("SELECT username FROM users LIMIT 1;")
        user = cursor.fetchone()

        cursor.close()
      
        return jsonify({"health": "OK"}), 200
    
    except Exception as e: #any exception
        exc_info = sys.exc_info()
        logging.error(e)
        return jsonify({"health": "ERROR", "error": traceback.format_exception(*exc_info) }), 500
    finally:
        cursor.close()
        connection_pool.putconn(conn)

# Ensure proper cleanup of connections when app shuts down
@app.teardown_appcontext
def shutdown_session(exception=None):
    # This doesn't actually close the pool yet, just a hook for future cleanup
    pass

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=PORT, debug=True)
    finally:
        # Close all connections when the app shuts down
        if connection_pool:
            connection_pool.closeall()