from flask import Flask, render_template
from flask_socketio import SocketIO, emit, join_room
import sqlite3
import random
import string
import os
from questions import get_random_question

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret!"

socketio = SocketIO(app, async_mode="eventlet", cors_allowed_origins="*")

rooms = {}

# ================= DATABASE =================

def init_db():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS leaderboard (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            score INTEGER
        )
    """)
    conn.commit()
    conn.close()

def save_score(name, score):
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("INSERT INTO leaderboard (name, score) VALUES (?,?)", (name, score))
    conn.commit()
    conn.close()

def get_top_players():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("SELECT name, score FROM leaderboard ORDER BY score DESC LIMIT 5")
    data = c.fetchall()
    conn.close()
    return data

# ================= ROUTES =================

@app.route("/")
def home():
    return render_template("index.html")

# ================= SOCKET EVENTS =================

@socketio.on("create_room")
def create_room():
    room_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
    rooms[room_code] = {"players": {}, "question": ""}
    join_room(room_code)
    emit("room_created", room_code)

@socketio.on("join_room")
def join_existing(data):
    room = data["room"]
    name = data["name"]

    if room in rooms:
        join_room(room)
        rooms[room]["players"][name] = 0
        emit("system_message", f"{name} دخل الغرفة", to=room)
        emit("update_players", rooms[room]["players"], to=room)

@socketio.on("new_question")
def new_question(data):
    room = data["room"]
    level = data["level"]

    if room in rooms:
        q = get_random_question(level)
        rooms[room]["question"] = q
        emit("question", q, to=room)

@socketio.on("add_point")
def add_point(data):
    room = data["room"]
    name = data["name"]

    if room in rooms and name in rooms[room]["players"]:
        rooms[room]["players"][name] += 1
        emit("update_players", rooms[room]["players"], to=room)

@socketio.on("chat")
def chat(data):
    room = data["room"]
    msg = data["msg"]
    name = data["name"]

    if room in rooms and len(msg) <= 200:
        emit("chat", {"name": name, "msg": msg}, to=room)

@socketio.on("save_scores")
def save_scores(data):
    room = data["room"]

    if room in rooms:
        for name, score in rooms[room]["players"].items():
            save_score(name, score)

        emit("top_players", get_top_players(), to=room)

# ================= RUN =================

if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host="0.0.0.0", port=port)
