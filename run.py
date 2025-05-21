from app import create_app
from app.database import db

app = create_app()

with app.app_context():
    db.drop_all()
    db.create_all()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
