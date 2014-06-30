from flask import Flask, jsonify

app = Flask(__name__)
app.config.from_object('app.oozie.config')
from app import views
