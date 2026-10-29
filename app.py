from flask import Flask, render_template, request, redirect, session
import sqlite3
import random
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():

    return render_template("index.html")
