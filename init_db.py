from app import create_app, db
import os

def init_database():
    """Initialize the database"""
    app = create_app(os.environ.get('FLASK_ENV'))

    with app.app_context():
        db.create_all()
        print("Database tables created successfully!")

if __name__ == '__main__':
    init_database()
