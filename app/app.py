from flask import Flask
from utilities.db import db
from blueprints.main import main_bp

app = Flask(__name__)
app.config['DEBUG'] = True

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:postgres@db:5432/postgres"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

# регистрируем blueprint
app.register_blueprint(main_bp)

# создаём таблицы
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
