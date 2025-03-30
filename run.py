import os
from app import create_app
from app.database import db

app = create_app()

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))  # Usa a porta do ambiente se disponível
    app.run(host="0.0.0.0", port=port, debug=True)
