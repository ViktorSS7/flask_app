from flask import Flask, url_for, render_template, session, request

from pprint import pprint

from markupsafe import escape

app = Flask(__name__)
app.secret_key = 'asldfjasfu2398h92hf9'

users = []


@app.route('/')
def main():
    if 'counter' not in session:
        session['counter'] = 0
    session['counter'] += 1
    return 'Hello - %d' % session['counter']


@app.route('/register', methods=['GET', 'POST'])
def register():
    pass
