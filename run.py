import time
import pymysql
import os
import asyncio
from app import create_app
from app.models import db

app = create_app()

def wait_for_db(max_retries=30, retry_interval=2):
    """Wait for the database to be ready"""
    retries = 0
    
    while retries < max_retries:
        try:
            # Try to connect to the database
            if 'mysql' in app.config['SQLALCHEMY_DATABASE_URI']:
                # Extract connection details from URI
                uri = app.config['SQLALCHEMY_DATABASE_URI']
                host = uri.split('@')[1].split(':')[0]
                port = int(uri.split(':')[-1].split('/')[0])
                
                # Try a direct connection to MySQL
                conn = pymysql.connect(
                    host=host,
                    port=port,
                    user=os.getenv('MYSQL_USER', 'flask_user'),
                    password=os.getenv('MYSQL_PASSWORD', 'flask_password'),
                    database=os.getenv('MYSQL_DATABASE', 'flask_db')
                )
                conn.close()
                print("Database connection successful!")
                return True
            else:
                # For SQLite or other DBs, just proceed
                return True
                
        except Exception as e:
            print(f"Database not ready yet: {e}")
            retries += 1
            print(f"Retrying in {retry_interval} seconds... (Attempt {retries}/{max_retries})")
            time.sleep(retry_interval)
    
    print("Failed to connect to database after maximum retries")
    return False

if __name__ == '__main__':
    # Wait for the database to be ready
    if wait_for_db():
        # Create tables if they don't exist
        with app.app_context():
            db.create_all()
        
        # Run the application
        app.run(host='0.0.0.0', port=5000, debug=True)
    else:
        print("Could not start application due to database connection issues")
