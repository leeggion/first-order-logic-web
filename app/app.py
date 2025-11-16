from flask import Flask, jsonify
from db import db, User

app = Flask(__name__)

# URL для PostgreSQL через docker-compose
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:postgres@db:5432/postgres"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

@app.before_first_request
def create_tables():
    db.create_all()

@app.route("/")
def index():
    users = User.query.all()
    return jsonify([{"id": u.id, "name": u.name} for u in users])

@app.route("/add/<name>")
def add_user(name):
    u = User(name=name)
    db.session.add(u)
    db.session.commit()
    return {"status": "ok", "user": name}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
