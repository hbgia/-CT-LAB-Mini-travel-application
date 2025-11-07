import streamlit as st
import json, hashlib, os

USERS_FILE = "users.json"

def _load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    return {}

def _save_users(data):
    with open(USERS_FILE, "w") as f:
        json.dump(data, f, indent=2)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register(username, password):
    users = _load_users()
    if username in users:
        return False, "Username already exists."
    users[username] = {"password": hash_password(password), "history": []}
    _save_users(users)
    return True, "Registration successful."

def login(username, password):
    users = _load_users()
    if username not in users or users[username]["password"] != hash_password(password):
        return False, "Incorrect password or User not found."
    st.session_state["user"] = username
    st.session_state["messages"] = users[username].get("history", [])
    return True, f"Welcome back, {username}!"

def save_history():
    if "user" in st.session_state:
        users = _load_users()
        u = st.session_state["user"]
        users[u]["history"] = st.session_state.get("messages", [])
        _save_users(users)
