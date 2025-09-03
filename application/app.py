from flask import Flask, request, jsonify, abort
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"  # For demo, replace with MySQL URI for real use
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# --- Models ---
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)

# --- In-memory users ---
users = {"qa": "123"}
DEMO_TOKEN = "abc123"

# ✅ Create tables immediately at startup
with app.app_context():
    db.create_all()

# --- Authentication helper ---
def authenticate():
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        abort(401)
    token = auth_header.split(" ")[1]
    if token != DEMO_TOKEN:
        abort(403)

# --- Routes ---
@app.route("/")
def index():
    return "Hello, On-Demand Test Environment!"

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    if not data or "user" not in data or "pass" not in data:
        return jsonify({"error": "Missing credentials"}), 400
    username = data["user"]
    password = data["pass"]
    if users.get(username) == password:
        return jsonify({"token": DEMO_TOKEN})
    return jsonify({"error": "Invalid credentials"}), 401

@app.route("/tasks", methods=["POST"])
def create_task():
    authenticate()
    data = request.json
    if not data or "title" not in data:
        return jsonify({"error": "Missing title"}), 400
    task = Task(title=data["title"])
    db.session.add(task)
    db.session.commit()
    return jsonify({"id": task.id, "title": task.title}), 201

@app.route("/tasks", methods=["GET"])
def list_tasks():
    authenticate()
    tasks = Task.query.all()
    return jsonify([{"id": t.id, "title": t.title} for t in tasks])

@app.route("/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    authenticate()
    task = Task.query.get(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    data = request.json
    task.title = data.get("title", task.title)
    db.session.commit()
    return jsonify({"id": task.id, "title": task.title})

@app.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    authenticate()
    task = Task.query.get(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    db.session.delete(task)
    db.session.commit()
    return jsonify({"message": "Deleted"}), 200

# --- Run Server ---
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
